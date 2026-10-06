# Quickstart

## Prérequis

- Python 3.14.4 (version testée sous Windows).
- Le CSV PaySim téléchargé depuis Kaggle (`ealaxi/paysim1`), placé sous `archive/PS_20174392719_1491204439457_log.csv`.
- Le CSV est exclu de Git par `.gitignore`.

## Installer

À la racine du projet, dans PowerShell :

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Vérifier les tests

```powershell
python -m pytest
```

Les tests utilisent de petits jeux synthétiques et ne chargent pas le CSV PaySim complet.

## Lancer les analyses

```powershell
python notebooks/01_exploration.py
python notebooks/02_validation_temporelle.py
```

Le premier script réalise l'EDA, le partage aléatoire et la comparaison des modèles. Le second entraîne et évalue chronologiquement sur une période future. Chaque script peut prendre plusieurs minutes et enregistre ses figures dans `reports/figures/`.

Dans VS Code, les marqueurs `# %%` permettent également d'exécuter les cellules une par une avec l'extension Python/Jupyter.

## Structure

- `src/fraude/` : chargement, caractéristiques et choix du seuil.
- `notebooks/` : analyses pédagogiques et modélisation.
- `tests/` : tests unitaires.
- `docs/` : bilan et journal d'apprentissage.
- `reports/figures/` : graphiques produits.
