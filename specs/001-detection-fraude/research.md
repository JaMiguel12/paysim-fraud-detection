# Recherche et décisions

## Déséquilibre des classes

Les 8 213 fraudes représentent 0,1291 % du dataset complet. Après restriction à `TRANSFER` et `CASH_OUT`, le taux est 0,2965 %. Un prédicteur constant « normal » atteint environ 99,70 % d'accuracy sur la validation du périmètre tout en manquant toutes les fraudes. Le rappel, la précision fraude, la PR-AUC et la matrice de confusion sont donc nécessaires.

## Périmètre des transactions

PaySim place les fraudes observées dans `TRANSFER` et `CASH_OUT`. Le filtre conserve les 8 213 fraudes de ce dataset, mais la question devient « lesquelles de ces deux catégories sont frauduleuses? » et non « chaque transaction est-elle frauduleuse? ». Ce choix doit être explicite pour tout usage hors simulation.

## Décisions contre les fuites

`nameOrig`, `nameDest` et `isFlaggedFraud` ne sont pas des entrées. Les soldes `newbalanceOrig` et `newbalanceDest` servent à l'exploration seulement parce qu'ils sont postérieurs à la transaction. Le seuil est calculé sur validation.

## Comparaison des modèles

Les trois modèles ont reçu le même échantillon stratifié de 300 000 observations et ont été comparés sur la même validation. HistGradientBoosting obtient la meilleure PR-AUC observée, 0,8072, au seuil standard. Il est ensuite réentraîné sur le train complet.

Le résultat de test aléatoire avec seuil réglé sur validation est rappel 89,84 %, précision 46,21 % et PR-AUC 0,8818. Le critère de rappel >=90 % et précision >=70 % n'est pas atteint.

## Pourquoi ajouter une séparation temporelle

Le partage aléatoire peut mélanger des transactions d'heures antérieures et postérieures. La séparation temporelle utilise les steps 1–520 pour entraîner, 521–631 pour régler et 632–743 comme période future. Les taux de fraude sont respectivement 0,2178 %, 1,4993 % et 3,2966 %, révélant une dérive importante de prévalence.

Le test temporel donne rappel 87,86 %, précision 88,78 % et PR-AUC 0,9629. La prévalence étant différente du test aléatoire, ces scores ne s'interprètent pas comme une comparaison contrôlée entre algorithmes.

## Importance par permutation

Sur un échantillon de validation de 50 000 lignes, le mélange de `oldbalanceOrg` et de `amount` produit les plus fortes baisses de PR-AUC. Cela mesure une dépendance prédictive du modèle; cela ne prouve aucune causalité et peut être affecté par la corrélation entre variables.

## Limites

Données simulées, périmètre réduit à deux types de transactions, variation temporelle de la prévalence et objectifs métier non atteints. Les tests déjà observés ne sont pas réutilisés pour choisir un autre seuil.
