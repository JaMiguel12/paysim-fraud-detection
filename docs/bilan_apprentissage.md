# Bilan d'apprentissage — Détection de fraude PaySim

Ce document récapitule le travail réalisé et les notions rencontrées. Le projet utilise les transactions simulées PaySim pour explorer les données et construire un premier classifieur de fraude.

## 1. Où se trouve le projet

- Le cahier des charges est dans `PROJET_FRAUDE_MOBILE_MONEY_PAYSIM_SPEC_KIT.md`.
- Le CSV PaySim est dans `archive/PS_20174392719_1491204439457_log.csv`.
- Le code d'analyse, organisé en cellules VS Code `# %%`, est dans `notebooks/01_exploration.py`.
- La validation chronologique est dans `notebooks/02_validation_temporelle.py`.
- Les fonctions partagées sont dans `src/fraude/`; les tests sont dans `tests/`.
- Les consignes d'installation et d'exécution sont dans `README.md`; les versions sont dans `requirements.txt`.
- Les graphiques sont enregistrés dans `reports/figures/`.
- L'environnement Python du projet est isolé dans `.venv/`.

La création d'un véritable notebook `.ipynb` n'a pas abouti; le fichier `.py` avec cellules `# %%` sert donc de support pédagogique exécutable dans VS Code ou comme script.

## 2. Rôle des outils et niveau pratiqué

| Outil | Niveau pratiqué ici | Ce qu'il a permis de faire |
|---|---|---|
| **pandas** | Débutant : lecture et manipulation de tableaux | Charger le CSV avec `read_csv`, choisir les colonnes et les types, filtrer les transactions, créer des colonnes, regrouper avec `groupby`, calculer des comptes et des taux, séparer `X` et `y`. |
| **NumPy** | Débutant : calcul numérique vectorisé | Appliquer `np.log1p` aux montants pour le graphique et créer des bornes d'histogramme avec `np.linspace`. La transformation logarithmique ne modifie pas les montants d'origine. |
| **Matplotlib** | Débutant : graphiques de données | Produire des diagrammes en barres, histogrammes, courbes, matrice de confusion et courbes précision-rappel; enregistrer les images en PNG. |
| **scikit-learn** | Initiation à l'apprentissage supervisé | Découper les données, établir un modèle de référence, entraîner et comparer des classifieurs, mesurer leurs performances, sélectionner un seuil et calculer l'importance par permutation. |

Le code utilise aussi `pathlib` de la bibliothèque standard Python pour construire les chemins vers le CSV et les images.

## 3. Parcours étape par étape

### Étape 1 — Préparer l'environnement et repérer le CSV

Un environnement virtuel `.venv` a été créé afin d'isoler les bibliothèques du projet. pandas, NumPy, Matplotlib et scikit-learn y ont été installés. Le CSV existant fait environ 494 Mo.

### Étape 2 — Charger les données avec pandas

Le dataset contient **6 362 620 lignes** et 11 colonnes. Le script ne charge que huit colonnes utiles à l'exploration et à la modélisation, avec des types compacts (`int16`, `int8`, `float32` et `category`). Le DataFrame utilisé occupe environ **145,6 Mio** en mémoire.

Concepts pandas abordés :

- Un **DataFrame** est un tableau avec des lignes et des colonnes.
- `usecols` limite les colonnes lues; `dtype` choisit leur représentation en mémoire.
- La cible `isFraud` vaut 0 pour une transaction normale et 1 pour une fraude.
- La moyenne d'une colonne composée de 0 et de 1 correspond à la proportion de 1.

### Étape 3 — Explorer et visualiser

L'exploration complète a trouvé **8 213 fraudes**, soit **0,1291 %** des transactions originales. Les fraudes observées se trouvent dans les types `TRANSFER` et `CASH_OUT`.

Les graphiques produits et leur question :

1. `01_fraudes_par_type.png` : combien de fraudes par type? C'est un nombre, pas un taux.
2. `02_distribution_montants_log1p.png` : les montants des opérations normales et frauduleuses ont-ils la même distribution? NumPy applique `log1p(x) = log(1 + x)` pour rendre les très grandes valeurs moins écrasantes sur le graphique. Avec `density=True`, on compare les formes des distributions plutôt que leurs volumes.
3. `03_taux_fraude_par_heure.png` : comment varie la proportion de fraudes selon l'heure du cycle simulé? `step` va de 1 à 743; `(step - 1) % 24` donne une heure cyclique de 0 à 23. Ce n'est pas une heure réelle.
4. `04_comportement_soldes.png` : à quelle fréquence un solde est-il nul avant ou après une transaction? Dans PaySim, l'émetteur a un solde nul après l'opération pour 98,05 % des fraudes contre 56,68 % des opérations normales. Le destinataire avait un solde nul avant l'opération dans 65,15 % des fraudes contre 42,48 % des opérations normales.

Ces graphiques décrivent des associations dans une simulation; ils ne démontrent pas une causalité.

### Étape 4 — Préparer les caractéristiques avec pandas

Pour l'étude du modèle, le périmètre a été limité à `TRANSFER` et `CASH_OUT`. Il contient **2 770 409 opérations**, dont les 8 213 fraudes du dataset. Le futur classifieur ne porte donc pas sur les autres types.

Le code construit les caractéristiques suivantes :

- `heure` : heure du cycle calculée depuis `step`;
- `amount` : montant de la transaction;
- `oldbalanceOrg` : solde initial de l'émetteur;
- `oldbalanceDest` : solde initial du destinataire;
- `type_transfer` : indicateur numérique pour distinguer `TRANSFER` de `CASH_OUT`.

Dans scikit-learn, `X` contient ces caractéristiques et `y` contient la réponse à apprendre, `isFraud`. Les identifiants de comptes et `isFlaggedFraud` ne sont pas utilisés. Les soldes après transaction servent à l'exploration, mais pas au modèle final, car ils peuvent ne pas être disponibles avant la décision.

Une démonstration intermédiaire `X_demo` utilise aussi des indicateurs de soldes après transaction pour montrer la construction de colonnes. **Ces variables ne font pas partie de `FEATURES` et ne sont pas entraînées dans le modèle final.**

### Étape 5 — Séparer entraînement, validation et test

`train_test_split` a été utilisé deux fois avec `stratify` et `random_state=42` pour créer un partage 60/20/20 reproductible. La stratification conserve une proportion comparable de fraudes; elle ne rend pas les classes aussi nombreuses.

| Partition | Lignes | Fraudes | Taux de fraude |
|---|---:|---:|---:|
| Entraînement | 1 662 245 | 4 927 | 0,2964 % |
| Validation | 554 082 | 1 643 | 0,2965 % |
| Test | 554 082 | 1 643 | 0,2965 % |

L'entraînement sert à apprendre les paramètres. La validation sert à comparer les modèles et à choisir le seuil. Le test est gardé pour l'évaluation finale.

### Étape 6 — Comprendre le déséquilibre avec un modèle naïf

`DummyClassifier(strategy="most_frequent")` prédit toujours la classe normale. Sur la validation, il obtient **99,7035 % d'accuracy** mais **0 % de rappel fraude** : il manque les 1 643 fraudes.

C'est pourquoi l'accuracy seule est trompeuse avec une cible aussi rare. La matrice de confusion et les métriques liées à la classe fraude sont plus instructives.

### Étape 7 — Entraîner et comparer les modèles

Les trois modèles ont été comparés sur le même échantillon stratifié de **300 000 lignes du train** et sur la même validation. La validation n'a pas été échantillonnée. Les résultats ci-dessous utilisent le seuil standard 0,5.

| Modèle | Accuracy | Précision fraude | Rappel fraude | PR-AUC |
|---|---:|---:|---:|---:|
| Régression logistique | 91,3553 % | 2,8712 % | 85,7578 % | 0,1559 |
| Random Forest | 98,69 % | 16,60 % | 85,21 % | 0,7294 |
| HistGradientBoosting | 98,61 % | 16,82 % | 93,37 % | 0,8072 |

La régression logistique a été placée dans un pipeline avec `StandardScaler`, qui apprend à mettre les colonnes à une échelle comparable. `class_weight="balanced"` donne davantage de poids à la classe fraude rare. Random Forest et HistGradientBoosting sont des modèles à base d'arbres et ne nécessitent pas cette normalisation.

`average_precision_score` fournit la PR-AUC, une mesure du classement plus adaptée à une classe rare que l'accuracy. HistGradientBoosting est ressorti comme meilleur candidat sur la validation.

### Étape 8 — Choisir un seuil sur la validation

Un classifieur produit une probabilité; un **seuil** la transforme en alerte oui/non. Avec HistGradientBoosting réentraîné sur tout le train, `precision_recall_curve` a servi à choisir, sur validation, le seuil qui maximise la précision tout en exigeant au moins 90 % de rappel.

Le seuil obtenu est **0,868509**. Sur la validation : rappel **90,0183 %**, précision **46,8928 %**, avec 1 675 fausses alertes et 164 fraudes manquées.

### Étape 9 — Évaluer une fois sur le test

Le seuil a été figé avant l'évaluation finale. Résultats sur le test :

- accuracy : **99,6598 %**;
- précision fraude : **46,2116 %**;
- rappel fraude : **89,8357 %**;
- PR-AUC : **0,8818**;
- matrice de confusion : 550 721 vrais négatifs, 1 718 faux positifs, 167 faux négatifs et 1 476 vrais positifs.

Le rappel du test est proche, mais légèrement inférieur à l'objectif de 90 %. Il ne faut pas modifier le seuil en fonction de ce test; il faudrait repartir d'une nouvelle validation ou réserver un nouveau test pour mesurer une nouvelle stratégie.

### Étape 10 — Comprendre l'importance des variables

L'importance par permutation a été calculée sur un échantillon de **50 000 lignes de validation**, avec trois répétitions. Chaque caractéristique est mélangée, puis on mesure la baisse de PR-AUC. Les baisses moyennes obtenues sont :

| Caractéristique | Baisse moyenne de PR-AUC |
|---|---:|
| `oldbalanceOrg` | 0,866899 |
| `amount` | 0,848370 |
| `oldbalanceDest` | 0,396859 |
| `type_transfer` | 0,171312 |
| `heure` | 0,095065 |

Cela indique sur quelles colonnes le modèle s'appuie dans cette expérience; ce n'est pas une preuve de causalité. Des variables corrélées peuvent partager leur importance.

### Étape 11 — Tester une séparation chronologique

Le partage aléatoire précédent peut mélanger passé et futur. Une seconde expérience, dans `notebooks/02_validation_temporelle.py`, respecte l'ordre des steps et découpe les **743 heures distinctes** en trois périodes : 70 % des heures pour l'entraînement, les 15 % suivantes pour la validation et les 15 % finales pour le test futur. Les heures d'un même `step` ne sont jamais réparties entre plusieurs jeux.

| Partition | Steps | Lignes | Fraudes | Taux de fraude |
|---|---:|---:|---:|---:|
| Entraînement | 1–520 | 2 653 729 | 5 781 | 0,2178 % |
| Validation | 521–631 | 78 701 | 1 180 | 1,4993 % |
| Test futur | 632–743 | 37 979 | 1 252 | 3,2966 % |

Le taux de fraude varie fortement dans le temps. HistGradientBoosting, entraîné sur la première période, atteint **90,00 % de rappel** et **81,01 % de précision** à la validation; le seuil choisi est **0,884145**. Sur la période future indépendante, avec ce seuil figé, les résultats sont :

- précision : **88,78 %**;
- rappel : **87,86 %**;
- PR-AUC : **0,9629**;
- matrice de confusion : 36 588 vrais négatifs, 139 faux positifs, 152 faux négatifs et 1 100 vrais positifs.

La précision et la PR-AUC sont supérieures à celles du partage aléatoire, mais le taux de fraude du test temporel est aussi beaucoup plus élevé (3,30 % contre 0,30 % environ). Ces scores ne sont donc pas directement comparables : les métriques de précision et de précision-rappel dépendent notamment de la fréquence de la classe positive. Cette expérience illustre aussi la différence entre une séparation aléatoire et une évaluation sur une période future.

## 4. Où voir les graphiques

Les fichiers PNG se trouvent dans `reports/figures/` :

- `01_fraudes_par_type.png`
- `02_distribution_montants_log1p.png`
- `03_taux_fraude_par_heure.png`
- `04_comportement_soldes.png`
- `05_courbe_precision_rappel.png`
- `06_matrice_confusion_test.png`
- `07_precision_rappel_test.png`
- `08_importance_variables.png`
- `09_taux_fraude_temporel.png`
- `10_precision_rappel_validation_temporelle.png`
- `11_matrice_confusion_test_temporel.png`
- `12_precision_rappel_test_temporel.png`

## 5. Limites et prochaines étapes

- PaySim est simulé : les scores ne garantissent pas les mêmes performances chez un opérateur réel.
- Le modèle ne traite que `TRANSFER` et `CASH_OUT`.
- Le rappel du test aléatoire est de 89,84 % et celui du test temporel de 87,86 %, tous deux légèrement sous la cible de 90 %.
- L'expérience temporelle montre une forte variation du taux de fraude entre périodes; elle ne doit pas être résumée par un unique score sans tenir compte de cette variation.
- Aucun seuil ne doit être retouché en fonction d'un jeu de test déjà consulté.
- Les trois modèles ont d'abord été comparés sur un sous-échantillon d'entraînement pour limiter le coût. HistGradientBoosting a ensuite été réentraîné sur le train complet pour le résultat final.
- Les fonctions communes de chargement, préparation et choix du seuil sont maintenant séparées dans `src/fraude/`; quatre tests unitaires passent avec pytest.
- Le projet possède maintenant un README, des dépendances versionnées, un `.gitignore` qui exclut les CSV et un journal de questions pour guider l'apprentissage.
- L'API de scoring demeure optionnelle et n'a pas été construite.

## 6. Exécuter le script

Dans PowerShell, depuis la racine du projet :

```powershell
.\.venv\Scripts\python.exe notebooks\01_exploration.py
.\.venv\Scripts\python.exe notebooks\02_validation_temporelle.py
\.venv\Scripts\python.exe -m pytest
```

Chaque script relit le CSV, entraîne ses modèles et régénère ses graphiques; il peut prendre plusieurs minutes. Les versions installées sont figées dans `requirements.txt`. Jupyter est disponible pour l'exécution interactive des cellules VS Code; pytest vérifie le chargement, la préparation des variables et la sélection d'un seuil.
