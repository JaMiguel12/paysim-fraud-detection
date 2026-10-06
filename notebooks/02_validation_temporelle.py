# %% [markdown]
# # Validation temporelle PaySim
#
# Le partage aléatoire mélange passé et futur. Ici, nous respectons l'ordre du
# temps: le premier bloc sert à entraîner, le deuxième à choisir le seuil et le
# dernier à mesurer la performance sur une période future.

# %% [markdown]
# ## 1. Charger et préparer le périmètre
#
# Comme dans l'analyse précédente, on étudie seulement `TRANSFER` et `CASH_OUT`.
# Les caractéristiques sont disponibles avant la transaction; `isFraud` reste
# la cible et n'entre jamais dans `X`.

# %%
from pathlib import Path
import sys

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_score,
    recall_score,
)
from fraude.data import charger_paysim
from fraude.evaluation import choisir_seuil
from fraude.features import FEATURES, construire_variables

CHEMIN_CSV = RACINE / "archive" / "PS_20174392719_1491204439457_log.csv"
DOSSIER_FIGURES = RACINE / "reports" / "figures"

df = charger_paysim(
    CHEMIN_CSV,
    colonnes=["step", "type", "amount", "oldbalanceOrg", "oldbalanceDest", "isFraud"],
)
df = construire_variables(df)

# %% [markdown]
# ## 2. Définir les périodes dans l'ordre chronologique
#
# Les coupures sont choisies sur les **steps distincts**, pas sur les lignes:
# aucune heure simulée ne se retrouve donc dans deux partitions. Les fractions
# 70/15/15 désignent la part des heures disponibles; comme le nombre de
# transactions varie selon le step, elles ne donneront pas des partitions de
# même taille en nombre de lignes.

# %%
steps = np.sort(df["step"].unique())
position_fin_train = int(np.floor(len(steps) * 0.70))
position_fin_validation = int(np.floor(len(steps) * 0.85))
step_fin_train = steps[position_fin_train - 1]
step_fin_validation = steps[position_fin_validation - 1]

masque_train = df["step"] <= step_fin_train
masque_validation = (df["step"] > step_fin_train) & (
    df["step"] <= step_fin_validation
)
masque_test = df["step"] > step_fin_validation

partitions = {
    "Entraînement": masque_train,
    "Validation": masque_validation,
    "Test futur": masque_test,
}

print(f"Steps disponibles : {steps.min()} à {steps.max()} ({len(steps)} heures)")
print(f"Coupures : train jusqu'au step {step_fin_train}; validation jusqu'au step {step_fin_validation}")
print("\nRépartition chronologique :")
for nom, masque in partitions.items():
    partie = df.loc[masque]
    print(
        f"{nom:14} : {len(partie):>9,} lignes, "
        f"{int(partie['isFraud'].sum()):>5,} fraudes, "
        f"taux {partie['isFraud'].mean() * 100:.4f} %, "
        f"steps {partie['step'].min()} à {partie['step'].max()}"
    )

X_train = df.loc[masque_train, FEATURES]
y_train = df.loc[masque_train, "isFraud"]
X_val = df.loc[masque_validation, FEATURES]
y_val = df.loc[masque_validation, "isFraud"]
X_test = df.loc[masque_test, FEATURES]
y_test = df.loc[masque_test, "isFraud"]

# Le graphique montre le taux de fraude à chaque heure simulée.
taux_par_step = df.groupby("step", observed=True)["isFraud"].mean() * 100
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(taux_par_step.index, taux_par_step.values, color="#c44536", linewidth=1)
ax.axvline(step_fin_train, color="#457b9d", linestyle="--", label="Fin entraînement")
ax.axvline(step_fin_validation, color="#2a9d8f", linestyle="--", label="Fin validation")
ax.set_title("Évolution du taux de fraude au fil des steps")
ax.set_xlabel("Step (heure simulée)")
ax.set_ylabel("Fraudes parmi les transactions (%)")
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "09_taux_fraude_temporel.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 3. Entraîner sur le passé et choisir le seuil sur la validation
#
# Le modèle ne voit que les premières heures. La validation représente une
# période ultérieure et sert à choisir le seuil qui maximise la précision tout
# en exigeant un rappel minimum de 90 %.

# %%
modele_temporel = HistGradientBoostingClassifier(
    class_weight="balanced",
    max_iter=100,
    random_state=42,
)
modele_temporel.fit(X_train, y_train)
probabilites_val = modele_temporel.predict_proba(X_val)[:, 1]

RAPPEL_MINIMUM = 0.90
precisions_val, rappels_val, seuils_val = precision_recall_curve(
    y_val, probabilites_val
)
precisions_avec_seuil = precisions_val[:-1]
rappels_avec_seuil = rappels_val[:-1]
seuil_temporel = choisir_seuil(
    y_val,
    probabilites_val,
    rappel_minimum=RAPPEL_MINIMUM,
)
indice_seuil = int(np.flatnonzero(seuils_val == seuil_temporel)[0])
predictions_val = (probabilites_val >= seuil_temporel).astype("int8")

print("\nRésultats sur la validation temporelle :")
print(f"Seuil sélectionné : {seuil_temporel:.6f}")
print(
    f"Précision : {precision_score(y_val, predictions_val, zero_division=0):.4%}"
)
print(f"Rappel : {recall_score(y_val, predictions_val, zero_division=0):.4%}")
print(f"PR-AUC : {average_precision_score(y_val, probabilites_val):.4f}")

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(rappels_val, precisions_val, color="#457b9d")
ax.scatter(
    rappels_avec_seuil[indice_seuil],
    precisions_avec_seuil[indice_seuil],
    color="#c44536",
    label=f"Seuil choisi : {seuil_temporel:.4f}",
    zorder=3,
)
ax.axvline(RAPPEL_MINIMUM, color="#6c757d", linestyle="--", label="Rappel minimum (90 %)")
ax.set_title("Compromis précision-rappel — validation temporelle")
ax.set_xlabel("Rappel fraude")
ax.set_ylabel("Précision des alertes")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "10_precision_rappel_validation_temporelle.png", dpi=160)
plt.close(fig)

# %% [markdown]
# ## 4. Évaluer une seule fois sur la période future
#
# Le seuil est figé avant cette étape. Le dernier bloc temporel sert à mesurer
# la performance sur des heures que le modèle n'a pas vues pendant son
# entraînement. On compare les résultats à ceux du partage aléatoire, en gardant
# à l'esprit que le taux de fraude des périodes est très différent.

# %%
probabilites_test = modele_temporel.predict_proba(X_test)[:, 1]
predictions_test = (probabilites_test >= seuil_temporel).astype("int8")
matrice_test = confusion_matrix(y_test, predictions_test, labels=[0, 1])

print("\nRésultats sur le test temporel (période future) :")
print(f"Accuracy : {accuracy_score(y_test, predictions_test):.4%}")
print(f"Précision : {precision_score(y_test, predictions_test, zero_division=0):.4%}")
print(f"Rappel : {recall_score(y_test, predictions_test, zero_division=0):.4%}")
print(f"PR-AUC : {average_precision_score(y_test, probabilites_test):.4f}")
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
ax.set_title("Matrice de confusion — test temporel")
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "11_matrice_confusion_test_temporel.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 6))
PrecisionRecallDisplay.from_predictions(
    y_test,
    probabilites_test,
    name="HistGradientBoosting temporel",
    ax=ax,
)
ax.set_title("Courbe précision-rappel — test temporel")
fig.tight_layout()
fig.savefig(DOSSIER_FIGURES / "12_precision_rappel_test_temporel.png", dpi=160)
plt.close(fig)

print("\nGraphiques temporels enregistrés dans reports/figures/")