# Plan : détection de fraude PaySim

## Environnement

- Python 3.14.4 (version utilisée pour les exécutions validées).
- pandas pour charger, filtrer, grouper et préparer les tableaux.
- NumPy pour les calculs numériques de l'exploration.
- Matplotlib pour les graphiques.
- scikit-learn pour les partitions, modèles et métriques.
- pytest pour les tests unitaires.
- Dépendances fixées dans `requirements.txt`.

## Architecture réalisée

- `src/fraude/data.py` : chargement sélectif du CSV avec types compacts.
- `src/fraude/features.py` : filtre `TRANSFER`/`CASH_OUT`, variables dérivées et séparation X/y.
- `src/fraude/evaluation.py` : sélection du seuil sous contrainte de rappel.
- `notebooks/01_exploration.py` : cellules VS Code pour l'EDA, le partage aléatoire, la comparaison, le seuil et le test.
- `notebooks/02_validation_temporelle.py` : entraînement passé, réglage sur période suivante, test futur.
- `tests/` : vérification du chargement, des caractéristiques et de la sélection d'un seuil.
- `reports/figures/` : artefacts PNG.

## Décisions de conception

1. Charger seulement huit colonnes pour l'EDA et sélectionner les colonnes dans l'expérience temporelle; représenter le texte en `category`, les montants en `float32` et les étiquettes en `int8`.
2. Exclure les identifiants, `isFlaggedFraud` et les soldes après transaction des caractéristiques du modèle.
3. Restreindre l'expérience de classification à `TRANSFER` et `CASH_OUT`, car les fraudes PaySim observées n'apparaissent que dans ces catégories. Cela restreint aussi le domaine de prédiction.
4. Comparer trois modèles sur le même échantillon stratifié de 300 000 lignes et la même validation; réentraîner HistGradientBoosting sur le train complet avant le test aléatoire.
5. Utiliser rappel, précision fraude, PR-AUC et matrice de confusion; ne pas optimiser l'accuracy seule.
6. Sélectionner le seuil qui maximise la précision avec rappel >= 90 % sur validation.
7. Ajouter une expérience temporelle distincte par tranches de steps, car la prévalence change fortement dans le temps.
8. Ignorer CSV, environnements et fichiers joblib dans Git.

## Vérification

Les tests pytest, les deux scripts et leurs diagnostics ont été exécutés sur l'environnement configuré. Les résultats et leurs limites sont détaillés dans le README et le bilan pédagogique.
