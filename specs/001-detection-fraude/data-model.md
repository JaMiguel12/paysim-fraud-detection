# Modèle de données

## Source

PaySim, fichier CSV simulé contenant 6 362 620 transactions et 11 colonnes. Une ligne représente une transaction; `isFraud` indique la cible binaire.

Le chargeur réutilisable est `src/fraude/data.py`. Types appliqués : `step` en `int16`, `type` en `category`, montants et soldes en `float32`, cible en `int8`.

## Colonnes chargées

| Colonne | Usage | Commentaire |
|---|---|---|
| `step` | Exploration et dérivation | Heure simulée depuis le début. `heure = (step - 1) % 24` représente un cycle, pas une heure réelle. |
| `type` | Filtre et variable dérivée | Seules les catégories `TRANSFER` et `CASH_OUT` entrent dans le modèle. |
| `amount` | Caractéristique | Montant de la transaction; `log1p` est utilisé uniquement pour visualiser sa distribution. |
| `oldbalanceOrg` | Caractéristique | Solde initial de l'émetteur, disponible avant transaction dans ce scénario. |
| `newbalanceOrig` | Exploration seulement | Solde après transaction, écarté des caractéristiques du modèle. |
| `oldbalanceDest` | Caractéristique | Solde initial du destinataire. |
| `newbalanceDest` | Exploration seulement | Solde après transaction, écarté des caractéristiques du modèle. |
| `isFraud` | Cible `y` | Réponse à prédire; ne figure jamais dans `X`. |

## Colonnes non chargées

- `nameOrig` et `nameDest` : identifiants de comptes, non employés comme variables. L'indicateur de type marchand issu de `nameDest` n'est pas utilisé dans la version actuelle.
- `isFlaggedFraud` : alerte dérivée d'une règle du simulateur, exclue pour éviter une fuite de cible.

## Caractéristiques du modèle

| Caractéristique | Construction | Type/intention |
|---|---|---|
| `heure` | `(step - 1) % 24` | Heure du cycle simulé, `int8`. |
| `amount` | Valeur source | Montant, `float32`. |
| `oldbalanceOrg` | Valeur source | Solde initial émetteur, `float32`. |
| `oldbalanceDest` | Valeur source | Solde initial destinataire, `float32`. |
| `type_transfer` | `type == "TRANSFER"` | Indicateur 0/1, `int8`; 0 correspond à `CASH_OUT` après filtrage. |

La cible `y` est la colonne `isFraud` correspondante. Les mêmes caractéristiques sont utilisées pour les expériences aléatoire et temporelle.
