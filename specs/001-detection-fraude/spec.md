# Spécification : détection de fraude Mobile Money

## Résumé

Explorer les transactions PaySim et entraîner un classifieur qui ordonne les opérations `TRANSFER` et `CASH_OUT` selon leur risque de fraude, pour aider à prioriser une vérification humaine. Le dataset est simulé; le projet n'est pas un service de production.

## Scénarios utilisateur

### US1 — Comprendre les transactions (Priorité : P1)

En tant qu'apprenant analyste, je veux explorer le volume, les types, les montants, le temps et les soldes afin de comprendre les signaux visibles dans PaySim.

**Critères d'acceptation**
- Les dimensions, taux de fraude, valeurs manquantes et répartition des fraudes sont mesurés.
- Des graphiques lisibles montrent les fraudes par type, les montants, le taux par heure et les soldes.
- Les comptes et les taux sont clairement distingués.

### US2 — Préparer les variables (Priorité : P1)

En tant qu'apprenant, je veux construire des caractéristiques sans inclure la réponse ni des identifiants trompeurs.

**Critères d'acceptation**
- `X` et `y` sont séparés; `isFraud` est la cible.
- Les identifiants et `isFlaggedFraud` ne sont pas utilisés.
- Les choix de caractéristiques et le filtre des types sont expliqués.
- Un partage aléatoire stratifié et une variante chronologique sont disponibles.

### US3 — Comparer des modèles (Priorité : P2)

En tant qu'analyste, je veux comparer une baseline et plusieurs modèles sur des données communes.

**Critères d'acceptation**
- La baseline « classe majoritaire » expose le piège de l'accuracy.
- Une régression logistique, une Random Forest et HistGradientBoosting sont évalués.
- Les métriques comprennent précision fraude, rappel et PR-AUC.
- Le modèle retenu est choisi avec la validation, jamais le test.

### US4 — Régler un seuil (Priorité : P2)

En tant que responsable du contrôle, je veux choisir un seuil à partir d'un objectif de rappel.

**Critères d'acceptation**
- Le seuil maximise la précision sous une contrainte de rappel d'au moins 90 % sur validation.
- Le seuil est figé avant le test.
- Le compromis précision-rappel est représenté graphiquement.

### US5 — Évaluer et expliquer (Priorité : P3)

En tant que lecteur, je veux comprendre les erreurs, les variables importantes et les limites.

**Critères d'acceptation**
- Une matrice de confusion et une courbe précision-rappel sont produites sur le test.
- Une importance par permutation sur validation est commentée.
- Le README explique les résultats, les données simulées et les limites.

## Exigences fonctionnelles

- **FR-001** : charger le CSV avec des colonnes sélectionnées et des types économes en mémoire.
- **FR-002** : justifier les colonnes conservées, dérivées et écartées.
- **FR-003** : produire une analyse exploratoire chiffrée et illustrée.
- **FR-004** : créer des partitions aléatoires stratifiées et une expérimentation temporelle sans chevauchement des steps.
- **FR-005** : comparer au moins trois modèles avec les mêmes métriques et partitions.
- **FR-006** : choisir un seuil sur validation selon un objectif de rappel.
- **FR-007** : produire les métriques, la matrice de confusion et la courbe précision-rappel du test.
- **FR-008** : fixer les graines aléatoires et versionner les dépendances.

## Critères de succès mesurables

- **SC-001** : rappel test >= 90 % et précision fraude test >= 70 %.
- **SC-002** : PR-AUC du meilleur modèle nettement supérieure à la baseline.
- **SC-003** : un lecteur comprend le projet avec le README en moins de 10 minutes.
- **SC-004** : tests et scripts de reproduction se terminent sans erreur quand le CSV est disponible.

## État mesuré

SC-001 n'est pas atteint : le partage aléatoire donne 89,84 % de rappel et 46,21 % de précision; l'expérience temporelle donne 87,86 % de rappel et 88,78 % de précision. Les résultats temporels et aléatoires ont des prévalences différentes. Le seuil ne doit pas être modifié à partir des tests déjà consultés.

SC-004 est vérifié pour les quatre tests et les deux scripts sur l'environnement documenté. SC-002 reste à compléter en ajoutant une comparaison explicite de PR-AUC avec la baseline naïve.

## Hors périmètre

API de scoring en production, données réelles d'opérateur, déploiement cloud et décisions automatisées sans validation humaine.
