# Constitution du projet PaySim

## Principes

### 1. Reproductibilité

Les expériences fixent les aléas avec `random_state=42`. Les dépendances Python utilisées sont consignées dans `requirements.txt`. Les scripts et les commandes de reproduction sont documentés dans le README.

### 2. Pas de fuite de données

- `isFraud` est la cible et ne doit jamais être une caractéristique de `X`.
- Les identifiants `nameOrig`, `nameDest` et le signal `isFlaggedFraud` ne sont pas utilisés comme caractéristiques.
- Les transformations apprises sont ajustées sur le train seulement.
- Les modèles et seuils sont sélectionnés avec la validation; le seuil est figé avant l'évaluation du test.
- Les soldes après transaction peuvent révéler des informations futures et sont exclus des caractéristiques du modèle.

### 3. Mesures adaptées aux classes rares

L'accuracy seule ne permet pas d'évaluer une fraude rare. Les rapports présentent au minimum précision de la classe fraude, rappel, PR-AUC et matrice de confusion.

### 4. Baseline et comparaison équitable

Un modèle naïf est présenté avant les modèles appris. Les modèles candidats sont comparés avec les mêmes caractéristiques, le même échantillon d'entraînement et la même validation.

### 5. Honnêteté des résultats

PaySim est simulé. Le périmètre, les limites temporelles et les résultats qui n'atteignent pas les objectifs métier sont explicitement rapportés. Aucun résultat de validation ou de test ne doit être présenté comme une garantie en production.

### 6. Code pédagogique et vérifiable

Le code et les explications sont en français. Les fonctions de chargement, préparation et choix du seuil sont réutilisables dans `src/fraude/`; les règles importantes sont vérifiées par pytest.

### 7. Données privées au dépôt

Les fichiers CSV, environnements locaux et modèles sérialisés ne sont pas ajoutés à Git. Le README explique où placer le jeu téléchargé.

## Gouvernance

Toute évolution doit conserver ces principes. Si un objectif métier n'est pas atteint, on le documente et on conçoit une nouvelle validation avant de modifier le modèle; un test déjà consulté ne sert pas au réglage.
