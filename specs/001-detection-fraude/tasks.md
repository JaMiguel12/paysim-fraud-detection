# Tâches d'implémentation

`[x]` indique une tâche réalisée et vérifiée; `[ ]` indique un travail restant.

## Phase 1 — Structure et données

- [x] T001 Créer la structure `src/fraude/`, `notebooks/`, `tests/`, `docs/` et `reports/figures/`.
- [x] T002 Versionner les dépendances et ignorer CSV, environnements virtuels et modèles sérialisés.
- [x] T003 Documenter l'installation et la reproduction dans le README.
- [x] T004 Utiliser le CSV PaySim local sans le committer.
- [x] T005 Créer un chargeur avec `usecols` et des types compacts.
- [x] T006 Tester le chargement sur un petit CSV synthétique.

## Phase 2 — Exploration et préparation

- [x] T007 Explorer dimensions, types, données manquantes, classes et répartition par type.
- [x] T008 Produire graphiques de types, montants, heure et soldes.
- [x] T009 Créer les variables d'entrée et séparer `X` de `y`.
- [x] T010 Exclure identifiants, indicateur de fraude simulé et soldes après transaction des variables du modèle.
- [x] T011 Construire un partage aléatoire stratifié 60/20/20.
- [x] T012 Réaliser une expérience distincte de séparation chronologique.
- [x] T013 Tester le filtre, les variables dérivées et le seuil sur des exemples synthétiques.

## Phase 3 — Modélisation et mesure

- [x] T014 Établir une baseline DummyClassifier et montrer les limites de l'accuracy.
- [x] T015 Comparer la régression logistique, Random Forest et HistGradientBoosting sur des données communes.
- [x] T016 Choisir un seuil sur validation selon l'objectif de rappel.
- [x] T017 Évaluer une fois le modèle final sur le test aléatoire.
- [x] T018 Produire matrices de confusion et courbes précision-rappel.
- [x] T019 Mesurer l'importance par permutation sur un échantillon de validation.

## Phase 4 — Documents Spec Kit

- [x] T020 Ajouter constitution, spécification, plan, modèle de données, recherche et guide rapide.
- [x] T021 Relier les décisions et résultats aux tâches et exigences fonctionnelles.

## Phase 5 — Points ouverts

- [ ] T022 Ajouter la PR-AUC de la baseline naïve à la comparaison explicite de SC-002.
- [ ] T023 Si l'objectif métier doit absolument être atteint, définir une nouvelle stratégie avec validation et test indépendant; ne pas régler sur les tests observés.
- [ ] T024 Publier le dépôt Git sans données brutes.
- [ ] T025 API de scoring (optionnelle, hors périmètre de la version actuelle).
