# Détection de fraude Mobile Money — PaySim

Projet pédagogique de science des données : explorer des transactions Mobile Money simulées, préparer des caractéristiques et comparer des modèles de détection de fraude.

## Résumé

PaySim contient 6 362 620 transactions et 8 213 fraudes (0,1291 %). L'analyse se concentre sur `TRANSFER` et `CASH_OUT`, les deux types dans lesquels des fraudes apparaissent dans ce dataset. Les résultats restent ceux d'une simulation et ne prédisent pas directement les performances d'un opérateur réel.

## Résultats

### Partage aléatoire stratifié

Les modèles ont d'abord été comparés sur un échantillon commun de 300 000 transactions d'entraînement, puis évalués sur la validation. Le meilleur classement obtenu est celui de HistGradientBoosting.

| Modèle | PR-AUC validation | Précision fraude à 0,5 | Rappel fraude à 0,5 |
|---|---:|---:|---:|
| Régression logistique | 0,1559 | 2,87 % | 85,76 % |
| Random Forest | 0,7294 | 16,60 % | 85,21 % |
| HistGradientBoosting | 0,8072 | 16,82 % | 93,37 % |

HistGradientBoosting a ensuite été entraîné sur tout le jeu d'entraînement. Le seuil 0,868509, choisi sur la validation pour maximiser la précision avec un rappel d'au moins 90 %, donne sur le test : **89,84 % de rappel**, **46,21 % de précision** et **0,8818 de PR-AUC**. La matrice de confusion contient 1 718 fausses alertes et 167 fraudes manquées. Le rappel final est légèrement inférieur à l'objectif de 90 %; le seuil n'a pas été retouché à partir du test.

### Expérience temporelle

Une seconde expérience entraîne sur les steps 1–520, choisit le seuil sur 521–631 et évalue sur la période future 632–743. Le seuil 0,884145 donne sur le test temporel **87,86 % de rappel**, **88,78 % de précision** et **0,9629 de PR-AUC**.

Le taux de fraude varie de 0,22 % dans le train à 3,30 % sur le test futur. Les résultats temporels ne sont donc pas directement comparables aux résultats aléatoires, car la prévalence influence notamment la précision et la PR-AUC.

## Données et méthode

Le CSV PaySim n'est pas inclus dans le dépôt. Télécharger le jeu `ealaxi/paysim1` depuis Kaggle et placer le fichier sous :

```text
archive/PS_20174392719_1491204439457_log.csv
```

Les scripts lisent uniquement les colonnes utiles et utilisent des types numériques compacts. Les identifiants de comptes et `isFlaggedFraud` sont exclus. Les caractéristiques du modèle sont l'heure du cycle, le montant, les soldes initiaux de l'émetteur et du destinataire, et le type de transaction. Les soldes après transaction sont exclus du modèle car ils ne seraient pas toujours disponibles au moment de décider.

- `notebooks/01_exploration.py` : analyse exploratoire, préparation, comparaison des modèles, seuil et test aléatoire.
- `notebooks/02_validation_temporelle.py` : entraînement et test chronologiques sur une période future.
- `src/fraude/` : fonctions réutilisables pour charger les données, construire les caractéristiques et choisir le seuil.
- `tests/` : tests unitaires rapides sur petits exemples, sans chargement du CSV complet.
- `docs/bilan_apprentissage.md` : explication pédagogique pas à pas.
- `docs/journal_apprentissage.md` : questions pour reformuler les notions apprises.
- `.specify/memory/constitution.md` : principes permanents du projet.
- `specs/001-detection-fraude/` : spécification, plan, tâches, modèle de données, recherche et guide rapide associés à l'implémentation.
- `reports/figures/` : graphiques générés par les scripts.

Les documents Spec Kit sont intégrés à partir de l'état actuel du projet. Ils consignent aussi les critères qui restent à atteindre; les résultats du test ne sont pas présentés comme satisfaisant l'objectif métier.

## Installation

Testé avec Python 3.14.4 sous Windows. Depuis la racine du projet, dans PowerShell :

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si `py -3.14` n'est pas disponible, créer l'environnement avec un interpréteur Python compatible installé sur la machine, puis sélectionner `.venv` comme interpréteur Python dans VS Code.

## Exécution

Exécuter les tests unitaires :

```powershell
python -m pytest
```

Lancer les cellules dans VS Code avec les commandes **Run Cell**, ou exécuter les scripts complets depuis la racine :

```powershell
python notebooks/01_exploration.py
python notebooks/02_validation_temporelle.py
```

Les scripts relisent le CSV, entraînent leurs modèles et régénèrent leurs graphiques; leur exécution peut prendre plusieurs minutes. Les fichiers `.csv`, l'environnement virtuel et les modèles sérialisés sont exclus de Git.

## Limites

- PaySim est simulé; les scores sont susceptibles d'être plus optimistes que sur des transactions réelles.
- Le modèle étudié ne couvre que `TRANSFER` et `CASH_OUT`.
- Le partage aléatoire et le partage temporel répondent à des questions différentes; la fraude est nettement plus fréquente dans la période temporelle future testée.
- Le rappel est inférieur à 90 % sur les deux tests finaux. Il ne faut pas régler un seuil en fonction d'un test déjà observé.
- Une importance par permutation indique l'utilité prédictive d'une colonne pour ce modèle, pas une relation causale.
- Le projet n'est pas un système de détection en production et ne fournit pas d'API de scoring.
