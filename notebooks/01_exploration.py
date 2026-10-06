# %% [markdown]
# # Exploration des fraudes PaySim
#
# Cette analyse utilise pandas pour charger et résumer les données, NumPy pour
# transformer temporairement les montants, et Matplotlib pour les visualiser.
# Les images sont enregistrées dans `reports/figures/`.

# %% [markdown]
# ## 1. Charger les données
#
# `usecols` limite la lecture aux colonnes utiles aux graphiques. `dtype` choisit
# des représentations compactes: par exemple `float32` utilise moins de mémoire
# que `float64`. `df` est le DataFrame pandas, c'est-à-dire notre tableau.

# %%
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from fraude.data import charger_paysim
from fraude.evaluation import choisir_seuil
from fraude.features import FEATURES, construire_variables, preparer_xy

CHEMIN_CSV = RACINE / "archive" / "PS_20174392719_1491204439457_log.csv"
DOSSIER_FIGURES = RACINE / "reports" / "figures"

df = charger_paysim(CHEMIN_CSV)

print(f"Dimensions : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
print(f"Mémoire du DataFrame : {df.memory_usage(deep=True).sum() / 1024**2:.1f} Mio")
print(f"Taux de fraude : {df['isFraud'].mean() * 100:.4f} %")

# %% [markdown]
# ## 2. Combien de fraudes par type ?
#
# `groupby` rassemble les lignes par type de transaction, puis `sum` additionne
# les 0 et les 1 de `isFraud`: le résultat est donc un **nombre** de fraudes.
# Ce graphique ne montre pas le taux de fraude: un type très fréquent peut
# avoir beaucoup de fraudes simplement parce qu'il contient beaucoup d'opérations.

# %%
fraudes_par_type = (
    df.groupby("type", observed=True)["isFraud"]
    .sum()
    .sort_values(ascending=False)
)
print("Nombre de fraudes par type :")
print(fraudes_par_type.to_string())

fig, ax = plt.subplots(figsize=(9, 5))
fraudes_par_type.plot(
    kind="bar",
    ax=ax,
    color=["#c44536", "#2a9d8f", "#457b9d", "#e9c46a", "#6c757d"],
)
ax.set_title("Nombre de fraudes par type de transaction")
ax.set_xlabel("Type de transaction")
ax.set_ylabel("Nombre de fraudes")
ax.tick_params(axis="x", rotation=0)
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "01_fraudes_par_type.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 3. Comparer les montants avec `log1p`
#
# Les montants vont de petites à très grandes valeurs; les très gros montants
# écraseraient visuellement le reste. NumPy fournit `log1p(x) = log(1 + x)`:
# ajouter 1 permet aussi de traiter un montant nul. La transformation ci-dessous
# sert **uniquement au graphique**; la colonne `amount` de `df` reste inchangée.
#
# `density=True` met les deux distributions à une aire comparable. On compare
# donc leur forme, pas le nombre total de transactions de chaque classe.

# %%
assert (df["amount"] >= 0).all(), "Les montants négatifs nécessitent une autre transformation."

montants_normaux = np.log1p(df.loc[df["isFraud"] == 0, "amount"].to_numpy())
montants_frauduleux = np.log1p(df.loc[df["isFraud"] == 1, "amount"].to_numpy())
limite_x = np.log1p(df["amount"].max())
bornes = np.linspace(0, limite_x, 70)

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(
    montants_normaux,
    bins=bornes,
    density=True,
    alpha=0.65,
    label="Transactions normales",
    color="#457b9d",
)
ax.hist(
    montants_frauduleux,
    bins=bornes,
    density=True,
    alpha=0.65,
    label="Fraudes",
    color="#c44536",
)
ax.set_title("Distribution des montants (échelle log1p)")
ax.set_xlabel("log(1 + montant)")
ax.set_ylabel("Densité")
ax.legend()
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "02_distribution_montants_log1p.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 4. Le taux de fraude selon l'heure
#
# `step` est un compteur d'heures simulées, pas une heure réelle de la journée.
# Comme le premier pas vaut 1, `(step - 1) % 24` produit une heure de cycle de
# 0 à 23. La moyenne de `isFraud` dans chaque groupe donne le **taux** de fraude:
# chaque 1 compte comme une fraude et chaque 0 comme une transaction normale.

# %%
df["heure"] = (df["step"] - 1) % 24
taux_fraude_par_heure = (
    df.groupby("heure", observed=True)["isFraud"].mean().reindex(range(24)) * 100
)
print("Taux de fraude par heure du cycle (%):")
print(taux_fraude_par_heure.round(3).to_string())

fig, ax = plt.subplots(figsize=(10, 5))
taux_fraude_par_heure.plot(kind="line", marker="o", ax=ax, color="#c44536")
ax.set_title("Taux de fraude selon l'heure du cycle simulé")
ax.set_xlabel("Heure du cycle (0 à 23)")
ax.set_ylabel("Transactions frauduleuses (%)")
ax.set_xticks(range(24))
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "03_taux_fraude_par_heure.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 5. Observer les soldes
#
# On compare deux situations: le solde de l'émetteur est-il nul **après** la
# transaction? Le solde du destinataire était-il nul **avant**? La moyenne d'une
# colonne de booléens (`True` vaut 1, `False` vaut 0) donne ici une proportion.
# Ces motifs sont des indices descriptifs, pas une preuve de fraude. En pratique,
# les soldes après transaction peuvent aussi ne pas être disponibles au moment
# où il faudrait évaluer une opération.

# %%
df["orig_vide_apres"] = df["newbalanceOrig"] == 0
df["dest_vide_avant"] = df["oldbalanceDest"] == 0
resume_soldes = (
    df.groupby("isFraud", observed=True)[["orig_vide_apres", "dest_vide_avant"]]
    .mean()
    .mul(100)
    .rename(index={0: "Normale", 1: "Fraude"})
    .rename(
        columns={
            "orig_vide_apres": "Émetteur à zéro après (%)",
            "dest_vide_avant": "Destinataire à zéro avant (%)",
        }
    )
)
print("Proportion de transactions avec un solde à zéro :")
print(resume_soldes.round(2).to_string())

fig, ax = plt.subplots(figsize=(9, 5))
resume_soldes.plot(kind="bar", ax=ax, color=["#c44536", "#457b9d"])
ax.set_title("Soldes à zéro selon la classe de transaction")
ax.set_xlabel("Classe")
ax.set_ylabel("Transactions concernées (%)")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="Situation du solde")
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "04_comportement_soldes.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 6. Première préparation pour scikit-learn
#
# En apprentissage supervisé, `X` contient les **caractéristiques** données au
# modèle et `y` contient la **cible** qu'il devra apprendre à prédire. Ici, on
# garde toutes les transactions pour l'instant et on prépare quatre colonnes
# numériques. `heure` et les indicateurs de solde sont des variables dérivées.
# La cible `isFraud` ne doit jamais se retrouver dans `X`.
#
# Cette démonstration utilise des soldes après transaction pour illustrer la
# création de colonnes. Ces variables sont exploratoires et ne seront pas
# utilisées pour entraîner le modèle final, car elles peuvent révéler le futur.

# %%
FEATURES_DEMO = ["heure", "amount", "orig_vide_apres", "dest_vide_avant"]
X_demo = df[FEATURES_DEMO].copy()
y = df["isFraud"].copy()

print("Forme de X (transactions x caractéristiques) :", X_demo.shape)
print("Forme de y (une cible par transaction) :", y.shape)
print("Caractéristiques utilisées :", FEATURES_DEMO)
print("La cible est séparée de X :", "isFraud" not in X_demo.columns)
print("\nPremières lignes de X :")
print(X_demo.head().to_string(index=False))

# %% [markdown]
# ## 7. Préparer les données et les découper
#
# Le périmètre choisi est `TRANSFER` et `CASH_OUT`: dans PaySim, ce filtre garde
# les 8 213 fraudes observées, mais le futur modèle ne jugera pas les autres
# types de transaction. On crée des variables numériques à partir d'informations
# disponibles avant l'opération. On écarte volontairement les soldes `newbalance`
# car ils sont mesurés après l'opération.
#
# `stratify=y` conserve une proportion de fraudes similaire dans les trois jeux.
# Le jeu de validation servira plus tard à comparer les modèles et régler un
# seuil; le jeu de test sera gardé pour l'évaluation finale.

# %%
from sklearn.model_selection import train_test_split

df_modele = construire_variables(df)
X, y = preparer_xy(df_modele)

X_reste, X_test, y_reste, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)
X_train, X_val, y_train, y_val = train_test_split(
    X_reste, y_reste, test_size=0.25, stratify=y_reste, random_state=42
)

print("\nDécoupage stratifié :")
for nom, X_partie, y_partie in [
    ("Entraînement", X_train, y_train),
    ("Validation", X_val, y_val),
    ("Test", X_test, y_test),
]:
    print(
        f"{nom:12} : {len(X_partie):,} lignes, "
        f"{int(y_partie.sum()):,} fraudes ({y_partie.mean() * 100:.4f} %)"
    )

print("Caractéristiques finales :", FEATURES)
print("Valeurs manquantes dans X :", int(X.isna().sum().sum()))

# %% [markdown]
# ## 8. Modèle de référence: toujours prédire « normal »
#
# `DummyClassifier` ne cherche aucun motif dans les caractéristiques: avec
# `most_frequent`, il prédit toujours la classe la plus fréquente. C'est une
# référence utile pour vérifier qu'un vrai modèle apprend quelque chose.
# On l'évalue sur la validation, pas sur le jeu de test réservé à la fin.
#
# L'accuracy mesure la proportion de prédictions correctes. Avec très peu de
# fraudes, elle peut être élevée même si aucune fraude n'est détectée. Le rappel
# mesure au contraire la proportion des fraudes réelles qui ont été retrouvées.

# %%
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score

modele_naif = DummyClassifier(strategy="most_frequent")
modele_naif.fit(X_train, y_train)
predictions_naives = modele_naif.predict(X_val)

accuracy_naive = accuracy_score(y_val, predictions_naives)
rappel_naif = recall_score(y_val, predictions_naives, zero_division=0)
matrice_naive = confusion_matrix(y_val, predictions_naives, labels=[0, 1])

print("\nModèle naïf évalué sur la validation :")
print(f"Accuracy : {accuracy_naive:.4%}")
print(f"Rappel fraude : {rappel_naif:.4%}")
print("Matrice de confusion (lignes = vrai, colonnes = prédit) :")
print(matrice_naive)

# %% [markdown]
# ## 9. Premier modèle: régression logistique
#
# La régression logistique apprend une probabilité de fraude à partir des
# caractéristiques. `StandardScaler` met les colonnes à des échelles comparables,
# car un montant peut être beaucoup plus grand que l'heure. Le pipeline ajuste
# ce scaler sur l'entraînement seulement, puis applique la même transformation
# à la validation.
#
# `class_weight="balanced"` augmente l'importance des fraudes rares pendant
# l'apprentissage. Ici, on garde le seuil standard de 0,5 pour découvrir le
# comportement du modèle; on choisira un seuil métier plus tard à partir de la
# validation. Pour comparer les modèles rapidement, chacun est entraîné sur le
# même échantillon stratifié de 300 000 lignes. La PR-AUC (`average_precision_score`)
# évalue le classement des transactions sur plusieurs seuils.

# %%
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

TAILLE_ECHANTILLON = 300_000
X_train_modele, _, y_train_modele, _ = train_test_split(
    X_train,
    y_train,
    train_size=TAILLE_ECHANTILLON,
    stratify=y_train,
    random_state=42,
)
print(f"\nÉchantillon commun d'entraînement des modèles : {len(X_train_modele):,} lignes")

modele_logistique = make_pipeline(
    StandardScaler(),
    LogisticRegression(class_weight="balanced", max_iter=200),
)
modele_logistique.fit(X_train_modele, y_train_modele)

probabilites_val = modele_logistique.predict_proba(X_val)[:, 1]
predictions_logistiques = (probabilites_val >= 0.5).astype("int8")

accuracy_logistique = accuracy_score(y_val, predictions_logistiques)
rappel_logistique = recall_score(y_val, predictions_logistiques, zero_division=0)
precision_logistique = precision_score(
    y_val, predictions_logistiques, zero_division=0
)
pr_auc_logistique = average_precision_score(y_val, probabilites_val)
matrice_logistique = confusion_matrix(
    y_val, predictions_logistiques, labels=[0, 1]
)

print("\nRégression logistique sur la validation (seuil 0,5) :")
print(f"Accuracy : {accuracy_logistique:.4%}")
print(f"Précision fraude : {precision_logistique:.4%}")
print(f"Rappel fraude : {rappel_logistique:.4%}")
print(f"PR-AUC : {pr_auc_logistique:.4f}")
print("Matrice de confusion (lignes = vrai, colonnes = prédit) :")
print(matrice_logistique)

# %% [markdown]
# ## 10. Comparer trois modèles sur les mêmes données
#
# La régression logistique apprend une frontière linéaire et a besoin de colonnes
# mises à l'échelle. Les arbres découpent les données par règles successives; ils
# n'ont généralement pas besoin de `StandardScaler`. On entraîne les deux modèles
# d'arbres sur le même échantillon que la régression et on compare leurs scores
# sur la même validation, au seuil 0,5. La PR-AUC compare leur capacité de
# classement indépendamment de ce seuil.

# %%
resultats_modeles = {
    "Régression logistique": {
        "Accuracy": accuracy_logistique,
        "Précision fraude": precision_logistique,
        "Rappel fraude": rappel_logistique,
        "PR-AUC": pr_auc_logistique,
    }
}

modeles_arbres = {
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    ),
    "HistGradientBoosting": HistGradientBoostingClassifier(
        class_weight="balanced",
        max_iter=100,
        random_state=42,
    ),
}

for nom, modele in modeles_arbres.items():
    modele.fit(X_train_modele, y_train_modele)
    probabilites_modele = modele.predict_proba(X_val)[:, 1]
    predictions_modele = (probabilites_modele >= 0.5).astype("int8")
    resultats_modeles[nom] = {
        "Accuracy": accuracy_score(y_val, predictions_modele),
        "Précision fraude": precision_score(
            y_val, predictions_modele, zero_division=0
        ),
        "Rappel fraude": recall_score(
            y_val, predictions_modele, zero_division=0
        ),
        "PR-AUC": average_precision_score(y_val, probabilites_modele),
    }
    print(f"Modèle terminé : {nom}")

tableau_modeles = pd.DataFrame.from_dict(resultats_modeles, orient="index")
tableau_modeles = tableau_modeles.sort_values("PR-AUC", ascending=False)
print("\nComparaison sur la validation (seuil 0,5) :")
print(tableau_modeles.to_string(float_format=lambda valeur: f"{valeur:.4f}"))

# %% [markdown]
# ## 11. Réentraîner le modèle retenu et choisir son seuil
#
# HistGradientBoosting a obtenu la meilleure PR-AUC pendant la comparaison.
# On le réentraîne maintenant sur tout le jeu d'entraînement. Ses probabilités
# peuvent différer de celles du modèle entraîné sur 300 000 lignes; il faut donc
# recalculer le seuil avec la validation.
#
# Le modèle renvoie une probabilité, puis le seuil transforme cette probabilité
# en alerte oui/non. Abaisser le seuil détecte généralement davantage de fraudes,
# mais augmente aussi les fausses alertes. On cherche ici, sur la validation, le
# seuil qui maximise la précision tout en gardant un rappel d'au moins 90 %.
# Ce seuil ne sera pas réglé sur le jeu de test.

# %%
from sklearn.metrics import precision_recall_curve

modele_final = HistGradientBoostingClassifier(
    class_weight="balanced",
    max_iter=100,
    random_state=42,
)
modele_final.fit(X_train, y_train)
probabilites_val_final = modele_final.predict_proba(X_val)[:, 1]

RAPPEL_MINIMUM = 0.90
precisions, rappels, seuils = precision_recall_curve(
    y_val, probabilites_val_final
)

seuil_choisi = choisir_seuil(
    y_val,
    probabilites_val_final,
    rappel_minimum=RAPPEL_MINIMUM,
)
predictions_val_finales = (probabilites_val_final >= seuil_choisi).astype("int8")

precision_val_finale = precision_score(
    y_val, predictions_val_finales, zero_division=0
)
rappel_val_final = recall_score(
    y_val, predictions_val_finales, zero_division=0
)
matrice_val_finale = confusion_matrix(
    y_val, predictions_val_finales, labels=[0, 1]
)

print("\nSeuil final choisi sur la validation pour un rappel >= 90 % :")
print(f"Seuil : {seuil_choisi:.6f}")
print(f"Précision fraude : {precision_val_finale:.4%}")
print(f"Rappel fraude : {rappel_val_final:.4%}")
print("Matrice de confusion (lignes = vrai, colonnes = prédit) :")
print(matrice_val_finale)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(rappels, precisions, color="#457b9d", label="HistGradientBoosting")
ax.scatter(
    rappel_val_final,
    precision_val_finale,
    color="#c44536",
    zorder=3,
    label=f"Seuil choisi : {seuil_choisi:.4f}",
)
ax.axvline(RAPPEL_MINIMUM, color="#6c757d", linestyle="--", label="Rappel minimum (90 %)")
ax.set_title("Compromis précision-rappel sur la validation")
ax.set_xlabel("Rappel fraude")
ax.set_ylabel("Précision des alertes")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "05_courbe_precision_rappel.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 12. Évaluation finale sur le test
#
# Le seuil est maintenant figé. On utilise le jeu de test une seule fois pour
# mesurer les performances finales; si les résultats déçoivent, on ne retouche
# pas le seuil à partir du test. La courbe précision-rappel du test sert au
# rapport final, pas à régler le modèle.

# %%
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay

probabilites_test = modele_final.predict_proba(X_test)[:, 1]
predictions_test = (probabilites_test >= seuil_choisi).astype("int8")

accuracy_test = accuracy_score(y_test, predictions_test)
precision_test = precision_score(y_test, predictions_test, zero_division=0)
rappel_test = recall_score(y_test, predictions_test, zero_division=0)
pr_auc_test = average_precision_score(y_test, probabilites_test)
matrice_test = confusion_matrix(y_test, predictions_test, labels=[0, 1])

print("\nÉvaluation finale sur le test (seuil figé) :")
print(f"Seuil : {seuil_choisi:.6f}")
print(f"Accuracy : {accuracy_test:.4%}")
print(f"Précision fraude : {precision_test:.4%}")
print(f"Rappel fraude : {rappel_test:.4%}")
print(f"PR-AUC : {pr_auc_test:.4f}")
print("Matrice de confusion (lignes = vrai, colonnes = prédit) :")
print(matrice_test)

fig, ax = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay.from_predictions(
    y_test,
    predictions_test,
    display_labels=["Normale", "Fraude"],
    values_format="d",
    ax=ax,
    colorbar=False,
)
ax.set_title("Matrice de confusion sur le test")
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "06_matrice_confusion_test.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 6))
PrecisionRecallDisplay.from_predictions(
    y_test,
    probabilites_test,
    name="HistGradientBoosting",
    ax=ax,
)
ax.set_title("Courbe précision-rappel sur le test")
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "07_precision_rappel_test.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 13. Comprendre les erreurs et les caractéristiques
#
# Dans la matrice de confusion, les faux positifs sont des opérations normales
# signalées à tort; les faux négatifs sont les fraudes manquées. Ici, le rappel
# dépend des faux négatifs et la précision des fausses alertes.
#
# Pour estimer l'utilité des variables, on mélange chaque colonne à tour de rôle
# sur un échantillon de validation et on mesure la baisse de PR-AUC. Une forte
# baisse indique que le modèle s'appuyait sur cette colonne. Ce n'est pas une
# preuve de causalité, et des variables corrélées peuvent se partager l'importance.

# %%
from sklearn.inspection import permutation_importance

X_validation_echantillon = X_val.sample(
    n=min(50_000, len(X_val)), random_state=42
)
y_validation_echantillon = y_val.loc[X_validation_echantillon.index]

importance = permutation_importance(
    modele_final,
    X_validation_echantillon,
    y_validation_echantillon,
    scoring="average_precision",
    n_repeats=3,
    random_state=42,
    n_jobs=1,
)
importance_variables = pd.Series(
    importance.importances_mean, index=FEATURES
).sort_values()

print("\nImportance par permutation sur un échantillon de validation :")
print(importance_variables.sort_values(ascending=False).to_string())

fig, ax = plt.subplots(figsize=(8, 5))
importance_variables.plot(kind="barh", ax=ax, color="#2a9d8f")
ax.set_title("Importance des variables (baisse de PR-AUC)")
ax.set_xlabel("Baisse moyenne de PR-AUC après mélange")
ax.set_ylabel("Caractéristique")
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "08_importance_variables.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 14. Limites à garder en tête
#
# - PaySim est simulé; ces résultats ne prédisent pas directement les résultats
#   d'un opérateur réel.
# - Le périmètre ne contient que `TRANSFER` et `CASH_OUT`; le modèle ne décide
#   pas si les autres types sont frauduleux.
# - Le découpage aléatoire ne teste pas encore la généralisation vers une période
#   future.
# - Le rappel du test (89,84 %) est légèrement inférieur à la cible de 90 %.
#   On ne modifie pas le seuil en fonction du test; une nouvelle tentative doit
#   être décidée à partir de la validation ou d'un nouveau jeu de test.

print("\nGraphiques enregistrés dans reports/figures/")