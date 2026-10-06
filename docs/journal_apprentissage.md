# Journal d'apprentissage

Utilise ce journal pour reformuler avec tes propres mots les concepts rencontrés. Ajoute une réponse après chaque séance avant de passer à la suite.

## Séance 1 — Charger et explorer avec pandas

- Qu'est-ce qu'un DataFrame?
- Pourquoi `usecols` et `dtype` réduisent-ils le coût mémoire?
- Quelle est la différence entre le nombre de fraudes et le taux de fraude?

## Séance 2 — Transformer et visualiser

- Que calcule `np.log1p(x)` et pourquoi l'utiliser dans un histogramme?
- À quoi sert `density=True` dans la comparaison des montants?
- Pourquoi une heure dérivée de `step` n'est-elle pas une heure réelle?

## Séance 3 — Préparer les données

- Que représentent `X` et `y`?
- Pourquoi `isFraud` doit-il être séparé des caractéristiques?
- À quoi sert la stratification? Pourquoi ne rend-elle pas les classes équilibrées?

## Séance 4 — Entraîner et évaluer

- Pourquoi le modèle naïf a-t-il une forte accuracy mais un rappel nul?
- Quelle différence entre précision et rappel?
- Que signifie `class_weight="balanced"`?

## Séance 5 — Choisir un seuil et tester

- Pourquoi choisir le seuil sur validation plutôt que sur test?
- Quel est le coût métier des faux positifs et des faux négatifs?
- Pourquoi le rappel mesuré sur test diffère-t-il légèrement de celui de validation?

## Séance 6 — Généraliser dans le temps

- Pourquoi un partage chronologique ressemble-t-il davantage à une prédiction du futur?
- Comment le taux de fraude a-t-il varié entre les trois périodes PaySim?
- Pourquoi faut-il interpréter la précision en tenant compte du taux de fraude?
