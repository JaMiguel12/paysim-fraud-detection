# Projet Data Science : détecter la fraude Mobile Money (PaySim)

**Guide complet pour débutant, organisé avec la méthode Spec Kit**

Ce fichier explique tout depuis zéro : ce qu'est le projet, ce que contiennent les données, comment fonctionne un modèle, puis comment dérouler le projet avec **Spec Kit** (constitution, spécification, plan, tâches, implémentation). Les blocs marqués « à coller » sont prêts à être donnés à ton agent de code.

---

## Sommaire

1. [Le projet en 2 minutes](#1-le-projet-en-2-minutes)
2. [Glossaire pour débutant](#2-glossaire-pour-débutant)
3. [Le dataset PaySim, expliqué](#3-le-dataset-paysim-expliqué)
4. [Les outils et leur rôle](#4-les-outils-et-leur-rôle)
5. [Spec Kit : la méthode](#5-spec-kit--la-méthode)
6. [Phase 0 : mise en place](#6-phase-0--mise-en-place)
7. [Phase 1 : la constitution](#7-phase-1--la-constitution)
8. [Phase 2 : la spécification](#8-phase-2--la-spécification-speckitspecify)
9. [Phase 3 : clarifier](#9-phase-3--clarifier-speckitclarify)
10. [Phase 4 : le plan technique](#10-phase-4--le-plan-technique-speckitplan)
11. [Phase 5 : les tâches](#11-phase-5--les-tâches-speckittasks)
12. [Phase 6 : vérifier la cohérence](#12-phase-6--vérifier-la-cohérence-speckitanalyze)
13. [Phase 7 : implémentation pas à pas](#13-phase-7--implémentation-pas-à-pas-speckitimplement)
14. [Comprendre les métriques](#14-comprendre-les-métriques)
15. [Pièges fréquents](#15-pièges-fréquents)
16. [Livrables, README et CV](#16-livrables-readme-et-cv)
17. [Bonus : API de scoring](#17-bonus--api-de-scoring)
18. [Plan de progression](#18-plan-de-progression)
19. [Check-list finale](#19-check-list-finale)

---

## 1. Le projet en 2 minutes

**Situation.** Un service d'argent mobile (comme Orange Money ou MTN MoMo) traite des millions de transactions. Parmi elles, une toute petite partie sont des **fraudes** : quelqu'un a pris de l'argent qui n'était pas à lui.

**Objectif.** Apprendre à un programme à **repérer les fraudes** à partir de transactions passées dont on connaît déjà le verdict (fraude ou pas).

**Principe du machine learning.** On montre au programme des centaines de milliers d'exemples avec leur réponse. Il découvre tout seul des motifs (par exemple « les fraudes vident souvent le compte en un seul retrait »). Ensuite on le teste sur des transactions qu'il n'a **jamais vues** pour savoir s'il a vraiment appris.

**Ce que tu vas faire, en 6 verbes :**

| Verbe | Ce que ça veut dire |
|---|---|
| Charger | Ouvrir le gros tableau de données dans Python |
| Explorer | Regarder, compter, tracer des graphiques pour comprendre |
| Préparer | Nettoyer, transformer les mots en nombres, créer des indices utiles |
| Entraîner | Laisser le programme apprendre sur une partie des données |
| Évaluer | Mesurer s'il trouve bien les fraudes sur l'autre partie |
| Conclure | Expliquer ce qui marche, ce qui ne marche pas, et pourquoi |

---

## 2. Glossaire pour débutant

| Mot | Explication simple |
|---|---|
| **Dataset** | Un gros tableau de données (comme un Excel avec des millions de lignes) |
| **Ligne** | Un exemple. Ici, une transaction |
| **Colonne / variable** | Une information sur chaque exemple (montant, type, heure…) |
| **Feature (caractéristique)** | Une colonne qu'on donne au modèle comme indice |
| **Cible (target, label)** | La colonne qu'on veut deviner. Ici `isFraud` (0 ou 1) |
| **Classification** | Deviner une catégorie (fraude / pas fraude) |
| **Modèle** | Le programme qui apprend à faire la prédiction |
| **Entraînement (fit)** | La phase où le modèle apprend sur des exemples |
| **Jeu d'entraînement (train)** | Les exemples utilisés pour apprendre |
| **Jeu de validation** | Des exemples gardés de côté pour **régler** le modèle |
| **Jeu de test** | Des exemples gardés de côté pour la **note finale**, qu'on ne touche qu'à la fin |
| **Surapprentissage** | Le modèle a appris les exemples par cœur et échoue sur des cas nouveaux |
| **Déséquilibre de classes** | Une catégorie est très rare (ici 1 fraude pour environ 800 transactions) |
| **Fuite de données (leakage)** | Le modèle reçoit, sans le vouloir, une information qui contient la réponse. Résultat : un score trop beau pour être vrai |
| **Seuil de décision** | Le modèle donne un risque entre 0 et 1. Au-dessus du seuil, on déclare « fraude » |
| **Analyse exploratoire (EDA)** | La phase où on regarde les données avant de modéliser |
| **Reproductibilité** | Relancer le projet donne exactement les mêmes résultats (grâce à `random_state`) |

---

## 3. Le dataset PaySim, expliqué

**PaySim** est un jeu de données **gratuit** de transactions Mobile Money, publié sur Kaggle (identifiant du jeu : `ealaxi/paysim1`). Il est **simulé** : un programme a généré les transactions en imitant le comportement d'un vrai service africain d'argent mobile. Il n'y a donc **aucune vraie personne** derrière, ce qui évite les problèmes de confidentialité.

### Chiffres clés (à vérifier toi-même à l'étape d'exploration)

- Environ **6,36 millions de lignes**, **11 colonnes**
- Environ **8 200 fraudes**, soit **0,13 %** des lignes
- Les fraudes n'existent que dans deux types de transaction : **TRANSFER** et **CASH_OUT**
- 1 unité de `step` = 1 heure, sur 30 jours (environ 743 steps)

### Les colonnes

| Colonne | Sens | Exemple |
|---|---|---|
| `step` | L'heure écoulée depuis le début (1 = première heure) | 1 |
| `type` | Le genre d'opération : `PAYMENT`, `TRANSFER`, `CASH_IN`, `CASH_OUT`, `DEBIT` | TRANSFER |
| `amount` | Le montant de la transaction | 181.0 |
| `nameOrig` | Identifiant du compte qui envoie | C1231006815 |
| `oldbalanceOrg` | Solde de l'émetteur **avant** | 181.0 |
| `newbalanceOrig` | Solde de l'émetteur **après** | 0.0 |
| `nameDest` | Identifiant du compte qui reçoit (`M...` = commerçant, `C...` = client) | C553264065 |
| `oldbalanceDest` | Solde du destinataire **avant** | 0.0 |
| `newbalanceDest` | Solde du destinataire **après** | 0.0 |
| `isFraud` | **La réponse.** 1 = fraude, 0 = normal | 1 |
| `isFlaggedFraud` | Alerte d'un règlement interne du simulateur (se déclenche très rarement) | 0 |

### Le scénario de fraude, en clair

Dans la simulation, un fraudeur prend le contrôle d'un compte, **transfère tout le solde** vers un autre compte, puis **retire l'argent en liquide** (CASH_OUT). C'est pourquoi la fraude apparaît seulement dans ces deux types, et pourquoi les soldes avant/après sont des indices très utiles. Tu le vérifieras dans l'exploration.

### Colonnes à ne PAS donner au modèle

- `nameOrig` : un identifiant n'est pas une information utile et ne se généralise pas.
- `isFlaggedFraud` : c'est une règle du simulateur liée directement à la fraude. L'utiliser reviendrait à tricher.
- `nameDest` : à ne pas utiliser tel quel. On peut seulement en tirer l'information « le destinataire est-il un commerçant (`M`) ? ».

### Où le télécharger

1. Crée un compte gratuit sur **Kaggle**.
2. Sur la page du jeu « PaySim1 » (`ealaxi/paysim1`), télécharge le CSV (environ 470 Mo).
3. Mets-le dans `data/raw/` (ce dossier ne sera **pas** envoyé sur GitHub).

---

## 4. Les outils et leur rôle

| Outil | Rôle dans le projet |
|---|---|
| **pandas** | Un « Excel dans Python » : charger le CSV, filtrer, grouper, créer des colonnes |
| **NumPy** | Calculs rapides sur des nombres (logarithmes, tableaux, seuils) |
| **Matplotlib** | Les graphiques (barres, histogrammes, courbes) |
| **scikit-learn** | Les modèles, le découpage des données, les métriques |
| **Jupyter / Colab** | Le cahier où on écrit le code par petits blocs et où on voit les résultats |
| **pytest** | Quelques tests automatiques pour vérifier que la préparation des données est correcte |
| **Git / GitHub** | Sauvegarder le projet et le montrer aux recruteurs |

---

## 5. Spec Kit : la méthode

**Spec Kit** est un outil open source de GitHub pour le **développement piloté par les spécifications** (« Spec-Driven Development »). L'idée : **on écrit d'abord ce qu'on veut et pourquoi**, ensuite comment le faire, ensuite la liste des tâches, et seulement après on produit le code.

### Les deux types de commandes

- **Commandes du terminal** : `specify init`, `specify check`… (elles préparent le projet)
- **Commandes « slash »** : `/speckit.xxx`, à taper **dans le chat de ton agent de code** (Claude Code, GitHub Copilot, Cursor…)

### Le déroulé

| Étape | Commande | Ce que ça produit | À quoi ça sert |
|---|---|---|---|
| 1 | `/speckit.constitution` | `.specify/memory/constitution.md` | Les règles du projet qui s'appliquent à tout |
| 2 | `/speckit.specify` | `specs/001-.../spec.md` | **Quoi et pourquoi** : le cahier des charges, sans technique |
| 3 | `/speckit.clarify` | Précisions ajoutées à `spec.md` | Lever les zones floues avant de planifier |
| 4 | `/speckit.plan` | `plan.md` (+ `research.md`, `data-model.md`) | **Comment** : technologies, structure, décisions |
| 5 | `/speckit.tasks` | `tasks.md` | La liste de tâches cochables |
| 6 | `/speckit.analyze` | Un rapport | Détecter les incohérences entre spec, plan et tâches |
| 7 | `/speckit.implement` | Le code | Exécuter les tâches une par une |

Trois points à retenir :
- La **spec** parle du besoin (le « quoi ») et ne cite pas de technologie. Le **plan** parle de la technique (le « comment »).
- La constitution est la loi du projet : tout le reste doit la respecter.
- L'ordre `clarify` puis `analyze` est une recommandation, pas une obligation.

### Installation (une seule fois)

Il te faut **Python**, **uv** (gestionnaire d'outils Python), **Git** et un **agent de code** compatible.

```bash
# Installer la commande specify
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Créer le projet (remplace "claude" par ton agent : copilot, cursor-agent, gemini...)
specify init paysim-fraude --ai claude

# Vérifier l'installation
cd paysim-fraude
specify check
```

> Selon la version, l'option s'appelle `--ai` ou `--integration`. En cas d'erreur, lance `specify init --help` pour voir la bonne syntaxe.

### Ce que `specify init` crée

```
paysim-fraude/
├── .specify/                 # modèles et scripts de Spec Kit
│   └── memory/
│       └── constitution.md   # la constitution du projet
├── specs/                    # un sous-dossier par fonctionnalité (créé par /speckit.specify)
│   └── 001-detection-fraude/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
└── (dossier de commandes de ton agent)
```

### Un conseil d'apprentissage important

Tu veux **apprendre** la data science, pas seulement obtenir un projet. Avec Spec Kit, l'agent peut écrire beaucoup de code à ta place. Pour que ça t'apprenne quelque chose :

1. **Lis chaque notebook généré** et demande à l'agent d'expliquer chaque ligne que tu ne comprends pas.
2. **Réécris à la main** au moins l'étape de préparation et l'évaluation.
3. Tiens un **journal d'apprentissage** (`docs/journal.md`) : une phrase par concept compris, avec ton exemple à toi.
4. À la fin, tu dois pouvoir expliquer le projet **sans regarder le code**. C'est ce qu'un recruteur testera.

---

## 6. Phase 0 : mise en place

### 6.1 Où travailler

- **Recommandé : en local** (VS Code + Jupyter). Spec Kit modifie des fichiers de ton dépôt, c'est plus simple en local.
- **Alternative : Google Colab** pour exécuter les notebooks (gratuit, rien à installer). Tu peux écrire les specs en local et lancer les notebooks dans Colab.
- Mémoire : le CSV complet pèse environ 470 Mo. Avec 8 Go de RAM c'est possible si tu réduis les types de données (voir étape de chargement).

### 6.2 Structure cible du dépôt

```
paysim-fraude/
├── .specify/ ...
├── specs/001-detection-fraude/ (spec.md, plan.md, tasks.md)
├── data/
│   └── raw/                  # le CSV (ignoré par Git)
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_preparation.ipynb
│   ├── 03_modelisation.ipynb
│   └── 04_evaluation.ipynb
├── src/fraude/
│   ├── __init__.py
│   ├── data.py               # chargement du CSV
│   ├── features.py           # création des variables
│   └── evaluation.py         # métriques et choix du seuil
├── tests/
│   └── test_data.py
├── reports/figures/          # les graphiques exportés
├── docs/journal.md           # ton journal d'apprentissage
├── requirements.txt
├── .gitignore
└── README.md
```

### 6.3 `requirements.txt`

```text
pandas
numpy
scikit-learn
matplotlib
jupyter
kagglehub
pytest
joblib
```

### 6.4 `.gitignore` (important : ne jamais envoyer le CSV sur GitHub)

```text
data/
*.csv
*.joblib
.ipynb_checkpoints/
__pycache__/
.venv/
```

---

## 7. Phase 1 : la constitution

La constitution fixe les règles du projet. Elle est lue avant chaque étape suivante.

**À coller dans l'agent :**

```text
/speckit.constitution Crée les principes du projet "détection de fraude Mobile Money sur PaySim" :

1. Reproductibilité : tout aléa est fixé (random_state=42), les versions des bibliothèques sont dans requirements.txt, le projet se relance de bout en bout avec les mêmes résultats.
2. Aucune fuite de données : les colonnes d'identifiants et isFlaggedFraud ne servent jamais de variables d'entrée ; tout rééquilibrage ou transformation est ajusté uniquement sur le jeu d'entraînement ; le jeu de test n'est utilisé qu'une seule fois, pour la note finale.
3. Métriques adaptées au déséquilibre : on n'utilise jamais la précision globale (accuracy) comme critère ; on suit le rappel, la précision de la classe fraude et la PR-AUC.
4. Simplicité d'abord : toujours commencer par un modèle de référence simple avant d'essayer un modèle plus complexe.
5. Honnêteté des résultats : les limites (données simulées, scores éventuellement trop optimistes) sont écrites dans le README.
6. Code lisible : fonctions réutilisables dans src/fraude/, notebooks propres et commentés en français, quelques tests pytest pour la préparation des données.
7. Données hors dépôt : le CSV n'est jamais commité ; le README explique comment le télécharger.
```

---

## 8. Phase 2 : la spécification (`/speckit.specify`)

Ici on décrit **le besoin**, sans citer de technologie.

**À coller dans l'agent :**

```text
/speckit.specify Construire un projet d'analyse et de modélisation qui détecte les transactions frauduleuses dans un jeu de données de transactions Mobile Money (PaySim, environ 6,3 millions de transactions dont environ 0,13 % de fraudes).

Contexte et objectif : un opérateur de Mobile Money veut repérer automatiquement les transactions suspectes pour les faire vérifier par une équipe humaine, en trouvant le maximum de fraudes tout en limitant les fausses alertes.

User stories :

US1 (priorité P1) - Comprendre les données
En tant qu'analyste, je veux explorer le jeu de données pour comprendre la répartition des transactions et des fraudes.
Scénarios d'acceptation :
- Je connais le nombre de transactions, de fraudes et le taux de fraude.
- Je sais dans quels types de transaction la fraude apparaît.
- Je dispose d'au moins 4 graphiques lisibles (fraudes par type, distribution des montants, fraude selon l'heure de la journée, comportement des soldes).

US2 (priorité P1) - Préparer des données propres et fiables
En tant qu'analyste, je veux un jeu de données prêt pour la modélisation, sans fuite d'information.
Scénarios d'acceptation :
- Les colonnes inutiles ou trompeuses sont retirées et justifiées.
- Les variables ajoutées sont documentées.
- Les données sont découpées en jeux d'entraînement, de validation et de test avec la même proportion de fraudes.

US3 (priorité P2) - Comparer des modèles de détection
En tant qu'analyste, je veux entraîner un modèle de référence puis plusieurs modèles et les comparer équitablement.
Scénarios d'acceptation :
- Un modèle de référence naïf montre pourquoi la précision globale est trompeuse.
- Au moins trois modèles sont comparés avec les mêmes données et les mêmes métriques.
- Le meilleur modèle est choisi sur le jeu de validation.

US4 (priorité P2) - Choisir un seuil de décision
En tant que responsable de la fraude, je veux choisir le seuil qui correspond à mon objectif (trouver au moins 90 % des fraudes).
Scénarios d'acceptation :
- Le seuil est choisi sur le jeu de validation, jamais sur le test.
- Le compromis entre fraudes trouvées et fausses alertes est montré sur une courbe.

US5 (priorité P3) - Expliquer et conclure
En tant que lecteur du projet, je veux comprendre quelles informations comptent le plus et quelles sont les limites.
Scénarios d'acceptation :
- Les variables les plus importantes sont classées et commentées.
- Un README présente le contexte, la méthode, les résultats chiffrés et les limites.

US6 (priorité P3, optionnelle) - Utiliser le modèle comme service
En tant que développeur, je veux interroger le modèle pour obtenir le risque de fraude d'une transaction.

Exigences fonctionnelles :
- FR-001 : le projet doit charger le jeu de données sans dépasser 8 Go de mémoire.
- FR-002 : le projet doit documenter chaque colonne utilisée ou écartée.
- FR-003 : le projet doit produire un rapport d'exploration chiffré et illustré.
- FR-004 : le projet doit séparer entraînement, validation et test en gardant la proportion de fraudes.
- FR-005 : le projet doit comparer au moins trois modèles avec les mêmes métriques (rappel, précision de la classe fraude, PR-AUC).
- FR-006 : le projet doit permettre de choisir et justifier un seuil de décision.
- FR-007 : le projet doit produire une matrice de confusion et une courbe précision-rappel sur le jeu de test.
- FR-008 : les résultats doivent être identiques à chaque exécution.

Critères de succès mesurables :
- SC-001 : le meilleur modèle atteint un rappel d'au moins 90 % avec une précision d'au moins 70 % sur le jeu de test (valeurs à ajuster après le modèle de référence).
- SC-002 : le meilleur modèle a une PR-AUC nettement supérieure à celle du modèle de référence.
- SC-003 : un lecteur extérieur comprend le projet en lisant le README en moins de 10 minutes.
- SC-004 : le projet se relance de bout en bout sans erreur à partir du README.

Cas limites :
- Valeurs manquantes ou soldes à zéro pour certains comptes.
- Types de transaction sans aucune fraude.
- Fraudes très rares dans un petit échantillon.

Hors périmètre : détection en temps réel en production, données réelles d'un opérateur, déploiement cloud.
```

---

## 9. Phase 3 : clarifier (`/speckit.clarify`)

Cette commande pose des questions pour lever les zones floues de la spec. Voici celles qui reviendront probablement, avec une réponse que je te conseille.

| Question | Réponse conseillée |
|---|---|
| Garde-t-on tous les types de transaction ? | Après vérification dans l'exploration, seulement `TRANSFER` et `CASH_OUT` (la fraude n'existe que là) |
| Quel découpage ? | 60 % entraînement, 20 % validation, 20 % test, stratifié. En bonus : une version « dans le temps » (entraînement sur les premiers jours, test sur les derniers) |
| Quelle métrique principale ? | La PR-AUC, complétée par le rappel et la précision de la classe fraude |
| Quel objectif métier pour le seuil ? | Trouver au moins 90 % des fraudes, avec la meilleure précision possible |
| Que fait-on de `isFlaggedFraud` ? | On l'ignore (c'est une règle du simulateur, pas un indice honnête) |
| Gère-t-on le déséquilibre comment ? | `class_weight="balanced"` d'abord ; un rééquilibrage des données uniquement sur l'entraînement en option |
| Et si la mémoire manque ? | Types de données réduits, puis échantillon de travail pour développer, jeu complet pour les résultats finaux |
| Les soldes « après » sont-ils disponibles au moment de décider ? | Dans la vraie vie pas toujours. On les utilise ici et on le **signale dans les limites** du README |

---

## 10. Phase 4 : le plan technique (`/speckit.plan`)

Ici on choisit les technologies et on explique **comment** faire.

**À coller dans l'agent :**

```text
/speckit.plan Stack : Python 3.12, pandas, NumPy, scikit-learn, Matplotlib, Jupyter ; tests avec pytest ; sauvegarde du modèle avec joblib. Aucun service payant.

Structure : code réutilisable dans src/fraude/ (data.py, features.py, evaluation.py), notebooks numérotés 01 à 04 dans notebooks/, graphiques exportés dans reports/figures/, tests dans tests/. Un fichier pytest.ini avec pythonpath = src.

Décisions techniques :
- Chargement : read_csv avec usecols et dtypes réduits (int16, int8, float32, category) pour tenir en mémoire ; la colonne nameDest sert seulement à créer l'indicateur dest_marchand puis est supprimée ; nameOrig n'est pas chargée.
- Périmètre de modélisation : après vérification dans l'exploration, ne garder que TRANSFER et CASH_OUT.
- Variables créées : heure de la journée (step % 24), type_transfer (0/1), erreur_solde_orig = oldbalanceOrg - amount - newbalanceOrig, erreur_solde_dest = oldbalanceDest + amount - newbalanceDest, orig_vide_apres (0/1), dest_vide_avant (0/1).
- Découpage : train_test_split stratifié en 60/20/20 avec random_state=42 ; variante temporelle en bonus.
- Modèles : DummyClassifier (référence), régression logistique avec StandardScaler, RandomForestClassifier, HistGradientBoostingClassifier, tous avec class_weight="balanced" quand c'est possible.
- Métriques : recall, precision de la classe fraude, average_precision_score (PR-AUC), matrice de confusion.
- Seuil : choisi sur la validation avec precision_recall_curve, objectif rappel >= 90 %.
- Interprétation : permutation_importance sur un échantillon de la validation.

Livrables du plan : data-model.md (colonnes d'origine, colonnes retirées, variables créées), research.md (justification des choix), quickstart.md (commandes pour tout relancer).
```

---

## 11. Phase 5 : les tâches (`/speckit.tasks`)

La commande génère `tasks.md`. Voici ce que tu dois obtenir, à peu près. `[P]` veut dire « peut se faire en parallèle », `[US1]` relie la tâche à une user story. L'agent cochera les cases `[X]` au fur et à mesure.

```markdown
## Phase 1 : Mise en place
- [ ] T001 Créer la structure du dépôt (src/fraude, notebooks, tests, data/raw, reports/figures, docs)
- [ ] T002 [P] Écrire requirements.txt, .gitignore et pytest.ini
- [ ] T003 [P] Écrire le README (squelette) et docs/journal.md
- [ ] T004 Télécharger PaySim dans data/raw/ (kagglehub ou manuellement)

## Phase 2 : Fondations
- [ ] T005 Écrire src/fraude/data.py : charger_paysim() avec dtypes réduits
- [ ] T006 [P] Écrire tests/test_data.py : forme et types du chargement

## Phase 3 : US1 Comprendre les données
- [ ] T007 [US1] Notebook 01 : taille, types, valeurs manquantes, doublons
- [ ] T008 [US1] Notebook 01 : taux de fraude et fraudes par type de transaction
- [ ] T009 [P] [US1] Graphique : fraudes par type
- [ ] T010 [P] [US1] Graphique : distribution des montants (échelle log), fraude vs normal
- [ ] T011 [P] [US1] Graphique : taux de fraude selon l'heure de la journée
- [ ] T012 [US1] Vérifier le comportement des soldes dans les fraudes (compte vidé, destinataire vide)

## Phase 4 : US2 Préparer les données
- [ ] T013 [US2] Écrire src/fraude/features.py : filtrage et variables créées
- [ ] T014 [P] [US2] Tests de features.py (pas de valeurs manquantes, calculs corrects)
- [ ] T015 [US2] Notebook 02 : découpage 60/20/20 stratifié
- [ ] T016 [P] [US2] Test : proportion de fraude conservée et aucun chevauchement entre jeux
- [ ] T017 [US2] Documenter data-model.md (colonnes retirées et variables créées)

## Phase 5 : US3 Comparer des modèles
- [ ] T018 [US3] Notebook 03 : modèle de référence (Dummy) et démonstration du piège de la précision globale
- [ ] T019 [P] [US3] Entraîner la régression logistique
- [ ] T020 [P] [US3] Entraîner la Random Forest
- [ ] T021 [P] [US3] Entraîner le Gradient Boosting
- [ ] T022 [US3] Tableau de comparaison sur la validation (PR-AUC, rappel, précision)

## Phase 6 : US4 Seuil de décision
- [ ] T023 [US4] Écrire choisir_seuil() dans src/fraude/evaluation.py
- [ ] T024 [US4] Courbe précision-rappel sur la validation avec le seuil choisi

## Phase 7 : US5 Évaluation finale et explication
- [ ] T025 [US5] Notebook 04 : évaluation unique sur le test (matrice de confusion, rapport)
- [ ] T026 [P] [US5] Importance des variables (permutation)
- [ ] T027 [US5] Rédiger conclusions et limites
- [ ] T028 [US5] Finaliser le README avec les chiffres réels

## Phase 8 : Finition
- [ ] T029 Relancer le projet de bout en bout et vérifier la reproductibilité
- [ ] T030 Publier sur GitHub (sans les données)
```

Si une tâche te paraît trop grosse ou trop floue, demande à l'agent de la découper avant de continuer.

---

## 12. Phase 6 : vérifier la cohérence (`/speckit.analyze`)

À lancer **après** `/speckit.tasks` et **avant** `/speckit.implement`. L'agent compare la spec, le plan et les tâches pour trouver ce qui manque ou se contredit.

Ce que tu dois vérifier dans son rapport :
- Chaque exigence (FR-001 à FR-008) est couverte par au moins une tâche.
- Chaque user story a ses tâches.
- Aucune tâche ne contredit la constitution (par exemple utiliser le test pour régler le seuil).
- Le seuil de rappel de 90 % apparaît bien dans la spec, le plan et les tâches.

---

## 13. Phase 7 : implémentation pas à pas (`/speckit.implement`)

Tu peux lancer `/speckit.implement` pour tout exécuter, ou **par groupes de tâches** (recommandé pour apprendre) :

```text
/speckit.implement tâches T001 à T006
```

Voici ce que fait chaque étape, avec le code à comprendre. Dans les notebooks, ajoute en haut :

```python
import sys
sys.path.append("../src")
```

### Étape A : télécharger les données

```python
import kagglehub
chemin_dossier = kagglehub.dataset_download("ealaxi/paysim1")
print(chemin_dossier)   # le dossier qui contient le CSV
```

Si Kaggle demande une connexion, télécharge le fichier à la main (voir section 3).

### Étape B : charger les données (`src/fraude/data.py`)

Le CSV est gros. On ne charge que les colonnes utiles et on utilise des types plus petits pour économiser la mémoire.

```python
import pandas as pd

COLONNES = ["step", "type", "amount", "oldbalanceOrg", "newbalanceOrig",
            "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud"]

DTYPES = {
    "step": "int16", "type": "category", "amount": "float32",
    "oldbalanceOrg": "float32", "newbalanceOrig": "float32",
    "oldbalanceDest": "float32", "newbalanceDest": "float32",
    "isFraud": "int8",
}

def charger_paysim(chemin_csv: str) -> pd.DataFrame:
    df = pd.read_csv(chemin_csv, usecols=COLONNES, dtype=DTYPES)
    # On garde seulement l'info "le destinataire est un commerçant ?" puis on supprime l'identifiant
    df["dest_marchand"] = df["nameDest"].str.startswith("M").astype("int8")
    return df.drop(columns=["nameDest"])
```

**Ce que tu apprends :** `usecols` (ne lire que certaines colonnes), `dtype` (réduire la mémoire), `.str.startswith` (travailler sur du texte dans pandas).

### Étape C : explorer (notebook 01)

```python
import glob
from fraude.data import charger_paysim

fichier = glob.glob(chemin_dossier + "/*.csv")[0]
df = charger_paysim(fichier)

print(df.shape)                       # (lignes, colonnes)
df.info(memory_usage="deep")          # types et mémoire
print(df.isnull().sum())              # valeurs manquantes
print(df.duplicated().sum())          # doublons

print(df["isFraud"].value_counts())               # combien de 0 et de 1
print(df["isFraud"].mean() * 100, "% de fraude")  # taux de fraude
print(df.groupby("type")["isFraud"].agg(["sum", "mean"]))   # fraudes par type
```

**Ce que tu dois observer :** la fraude est très rare, et elle n'existe que dans `TRANSFER` et `CASH_OUT`. C'est cette observation qui justifie le filtrage de l'étape D.

Les graphiques (Matplotlib) :

```python
import numpy as np
import matplotlib.pyplot as plt

# 1) Fraudes par type
df.groupby("type")["isFraud"].sum().plot(kind="bar")
plt.title("Nombre de fraudes par type de transaction")
plt.ylabel("Fraudes")
plt.tight_layout()
plt.show()

# 2) Montants : on prend le log pour que les gros montants n'écrasent pas le graphique
fig, ax = plt.subplots()
ax.hist(np.log1p(df.loc[df["isFraud"] == 0, "amount"]), bins=60, alpha=0.6, density=True, label="Normal")
ax.hist(np.log1p(df.loc[df["isFraud"] == 1, "amount"]), bins=60, alpha=0.6, density=True, label="Fraude")
ax.set_xlabel("log(1 + montant)")
ax.legend()
plt.show()

# 3) Taux de fraude selon l'heure de la journée
df["heure"] = df["step"] % 24
(df.groupby("heure")["isFraud"].mean() * 100).plot()
plt.ylabel("% de fraude")
plt.show()

# 4) Comportement des soldes dans les fraudes
fraudes = df[df["isFraud"] == 1]
print("Compte émetteur vidé :", (fraudes["newbalanceOrig"] == 0).mean())
print("Destinataire vide avant :", (fraudes["oldbalanceDest"] == 0).mean())
```

Pour chaque graphique, écris **une phrase** dans ton journal : « Ce que je vois, et ce que ça m'apprend ».

### Étape D : créer les variables (`src/fraude/features.py`)

On garde les types utiles et on ajoute des **indices** que le modèle ne pourrait pas deviner seul.

```python
import pandas as pd

FEATURES = [
    "heure", "amount", "oldbalanceOrg", "newbalanceOrig",
    "oldbalanceDest", "newbalanceDest",
    "erreur_solde_orig", "erreur_solde_dest",
    "orig_vide_apres", "dest_vide_avant", "type_transfer",
]

def construire_variables(df: pd.DataFrame) -> pd.DataFrame:
    # La fraude n'existe que dans ces deux types (constaté à l'étape C)
    df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])].copy()

    df["heure"] = (df["step"] % 24).astype("int8")
    df["type_transfer"] = (df["type"] == "TRANSFER").astype("int8")

    # Si tout est normal, ces deux "erreurs" valent 0. Une valeur différente est suspecte.
    df["erreur_solde_orig"] = df["oldbalanceOrg"] - df["amount"] - df["newbalanceOrig"]
    df["erreur_solde_dest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]

    df["orig_vide_apres"] = (df["newbalanceOrig"] == 0).astype("int8")
    df["dest_vide_avant"] = (df["oldbalanceDest"] == 0).astype("int8")
    return df
```

**Ce que tu apprends :** le **feature engineering** : fabriquer des colonnes plus parlantes que les colonnes brutes. C'est souvent ce qui fait la différence entre un modèle moyen et un bon modèle.

### Étape E : découper en trois paquets (notebook 02)

```python
from sklearn.model_selection import train_test_split
from fraude.features import construire_variables, FEATURES

df_modele = construire_variables(df)
X = df_modele[FEATURES]
y = df_modele["isFraud"]

# D'abord on met de côté 20 % pour le TEST (on n'y touche qu'à la fin)
X_tmp, X_test, y_tmp, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42)

# Puis on sépare le reste en ENTRAÎNEMENT (60 % du total) et VALIDATION (20 % du total)
X_train, X_val, y_train, y_val = train_test_split(
    X_tmp, y_tmp, test_size=0.25, stratify=y_tmp, random_state=42)

for nom, serie in [("train", y_train), ("val", y_val), ("test", y_test)]:
    print(nom, len(serie), "lignes,", round(serie.mean() * 100, 3), "% de fraude")
```

**Pourquoi trois paquets ?**
- **Entraînement** : le modèle apprend dessus.
- **Validation** : tu compares les modèles et tu règles le seuil dessus.
- **Test** : la note finale, utilisée **une seule fois**. Si tu règles quoi que ce soit en regardant le test, ta note finale est truquée sans que tu le saches.

`stratify=y` garantit que chaque paquet garde la même proportion de fraudes. `random_state=42` rend le découpage identique à chaque exécution.

### Étape F : le modèle de référence (notebook 03)

Avant tout, on montre **pourquoi la précision globale est trompeuse**.

```python
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, recall_score

dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
pred = dummy.predict(X_val)
print("Précision globale :", accuracy_score(y_val, pred))   # très haute
print("Rappel (fraudes trouvées) :", recall_score(y_val, pred))   # 0.0
```

Ce modèle répond toujours « pas de fraude ». Il a une très bonne précision globale et il ne trouve **aucune** fraude. Voilà pourquoi la constitution interdit d'utiliser l'accuracy comme critère.

### Étape G : entraîner et comparer les modèles

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score

modeles = {
    "Régression logistique": make_pipeline(
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=1000)),
    "Random Forest": RandomForestClassifier(
        n_estimators=100, max_depth=12, class_weight="balanced",
        n_jobs=-1, random_state=42),
    "Gradient Boosting": HistGradientBoostingClassifier(
        class_weight="balanced", random_state=42),
}

for nom, modele in modeles.items():
    modele.fit(X_train, y_train)
    proba = modele.predict_proba(X_val)[:, 1]     # risque de fraude entre 0 et 1
    print(f"{nom} : PR-AUC = {average_precision_score(y_val, proba):.4f}")
```

**À comprendre :**
- `StandardScaler` remet toutes les colonnes à la même échelle (utile pour la régression logistique, inutile pour les arbres).
- `class_weight="balanced"` dit au modèle : « une fraude manquée coûte beaucoup plus cher qu'une fausse alerte ».
- `predict_proba` donne un **risque** entre 0 et 1, pas un simple oui/non.
- Si l'entraînement est trop lent, développe d'abord sur un échantillon : `X_train.sample(300_000, random_state=42)` (et les `y` correspondants avec `.loc`).

Choisis le meilleur modèle **sur la validation** :

```python
meilleur_nom = "Gradient Boosting"      # remplace par celui qui a la meilleure PR-AUC
meilleur = modeles[meilleur_nom]
```

### Étape H : choisir le seuil (`src/fraude/evaluation.py`)

Le modèle donne un risque. À partir de quelle valeur déclare-t-on « fraude » ? Un seuil bas trouve plus de fraudes mais crée plus de fausses alertes.

```python
import numpy as np
from sklearn.metrics import precision_recall_curve

def choisir_seuil(y_vrai, proba, rappel_min=0.90):
    """Renvoie le seuil qui garde un rappel >= rappel_min avec la meilleure précision."""
    precision, rappel, seuils = precision_recall_curve(y_vrai, proba)
    precision, rappel = precision[:-1], rappel[:-1]      # alignés sur les seuils
    ok = rappel >= rappel_min
    if not ok.any():
        raise ValueError("Aucun seuil n'atteint le rappel demandé")
    i = np.argmax(np.where(ok, precision, -1))
    return seuils[i]
```

Utilisation, **sur la validation** :

```python
from fraude.evaluation import choisir_seuil

proba_val = meilleur.predict_proba(X_val)[:, 1]
seuil = choisir_seuil(y_val, proba_val, rappel_min=0.90)
print("Seuil choisi :", seuil)
```

### Étape I : la note finale sur le test (notebook 04)

Une seule fois, avec le seuil figé.

```python
from sklearn.metrics import (classification_report, confusion_matrix,
                             ConfusionMatrixDisplay, PrecisionRecallDisplay)
import matplotlib.pyplot as plt

proba_test = meilleur.predict_proba(X_test)[:, 1]
pred_test = (proba_test >= seuil).astype(int)

print(classification_report(y_test, pred_test, digits=4,
                            target_names=["Normal", "Fraude"]))

ConfusionMatrixDisplay(confusion_matrix(y_test, pred_test),
                       display_labels=["Normal", "Fraude"]).plot(values_format="d")
plt.show()

PrecisionRecallDisplay.from_predictions(y_test, proba_test)
plt.show()
```

### Étape J : quelles variables comptent le plus

```python
from sklearn.inspection import permutation_importance

echantillon = X_val.sample(50_000, random_state=42)
y_ech = y_val.loc[echantillon.index]

res = permutation_importance(meilleur, echantillon, y_ech,
                             scoring="average_precision", n_repeats=5,
                             random_state=42, n_jobs=-1)

import pandas as pd
importance = pd.Series(res.importances_mean, index=FEATURES).sort_values()
importance.plot(kind="barh")
plt.title("Importance des variables")
plt.tight_layout()
plt.show()
```

**Comment ça marche :** on mélange au hasard une colonne et on regarde de combien le score baisse. Plus il baisse, plus la colonne était importante.

### Étape K : sauvegarder le modèle

```python
import joblib
joblib.dump({"model": meilleur, "seuil": float(seuil), "features": FEATURES},
            "models/modele_fraude.joblib")
```

(Le dossier `models/` est ignoré par Git grâce à `*.joblib`.)

### Étape L : les tests pytest

`pytest.ini` :

```ini
[pytest]
pythonpath = src
```

`tests/test_data.py` :

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from fraude.features import construire_variables, FEATURES


def test_variables_creees_et_filtrage():
    df = pd.DataFrame({
        "step": [1, 2, 3],
        "type": pd.Categorical(["TRANSFER", "PAYMENT", "CASH_OUT"]),
        "amount": [100.0, 50.0, 200.0],
        "oldbalanceOrg": [100.0, 500.0, 200.0],
        "newbalanceOrig": [0.0, 450.0, 0.0],
        "oldbalanceDest": [0.0, 0.0, 1000.0],
        "newbalanceDest": [100.0, 0.0, 1200.0],
        "isFraud": [1, 0, 1],
    })
    out = construire_variables(df)
    assert len(out) == 2                                   # PAYMENT retiré
    assert out[FEATURES].isna().sum().sum() == 0           # aucune valeur manquante
    assert (out["erreur_solde_orig"] == 0).all()           # calcul correct


def test_decoupage_conserve_proportion_et_separe_les_jeux():
    n = 2000
    X = pd.DataFrame({"a": range(n)})
    y = pd.Series([1 if i % 20 == 0 else 0 for i in range(n)])   # 5 % de fraude
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42)
    assert abs(y_tr.mean() - y_te.mean()) < 0.01           # même proportion
    assert set(X_tr.index).isdisjoint(set(X_te.index))     # aucun chevauchement
```

Lance-les avec `pytest`. Ces tests montrent à un recruteur que tu contrôles la qualité de ta préparation de données.

### Variante « dans le temps » (bonus)

Dans la vraie vie, on entraîne sur le passé et on prédit le futur. Pour le simuler :

```python
coupure = df_modele["step"].quantile(0.8)
train = df_modele[df_modele["step"] <= coupure]
test = df_modele[df_modele["step"] > coupure]
```

Compare les résultats avec le découpage aléatoire et commente la différence.

---

## 14. Comprendre les métriques

### La matrice de confusion

|  | Le modèle dit « Normal » | Le modèle dit « Fraude » |
|---|---|---|
| **C'est vraiment normal** | Vrai négatif (bien) | **Faux positif** : fausse alerte |
| **C'est vraiment une fraude** | **Faux négatif** : fraude manquée | Vrai positif (bien) |

### Précision et rappel

- **Rappel** = parmi les **vraies fraudes**, combien le modèle en a trouvé ?
  `rappel = vrais positifs / (vrais positifs + faux négatifs)`
- **Précision** = parmi les **alertes** du modèle, combien étaient de vraies fraudes ?
  `précision = vrais positifs / (vrais positifs + faux positifs)`

### Exemple chiffré

Imagine 2 000 vraies fraudes dans le test. Le modèle déclenche 2 400 alertes :
- 1 800 sont de vraies fraudes (vrais positifs)
- 600 sont de fausses alertes (faux positifs)
- 200 fraudes n'ont pas été vues (faux négatifs)

Alors :
- Rappel = 1 800 / 2 000 = **90 %**
- Précision = 1 800 / 2 400 = **75 %**

Interprétation : on attrape 9 fraudes sur 10, et 3 alertes sur 4 sont justifiées.

### Le compromis

Baisser le seuil : on trouve plus de fraudes (rappel monte) mais on crée plus de fausses alertes (précision baisse). Monter le seuil : l'inverse. Le « bon » seuil dépend du coût d'une fraude manquée par rapport au coût de vérifier une fausse alerte. C'est une décision **métier**, pas seulement technique.

### La PR-AUC

L'aire sous la courbe précision-rappel. Elle résume la qualité du modèle sur **tous** les seuils à la fois. Pour une classe rare, elle est plus parlante que d'autres métriques classiques. Plus elle est proche de 1, mieux c'est.

---

## 15. Pièges fréquents

| Piège | Pourquoi c'est un problème | Comment l'éviter |
|---|---|---|
| Regarder la précision globale (accuracy) | Un modèle inutile peut avoir 99,87 % | Suivre rappel, précision de la classe fraude et PR-AUC |
| Garder `isFlaggedFraud` ou les identifiants | Fuite de données, score truqué | Les retirer et le justifier |
| Régler le seuil sur le test | La note finale est trop optimiste | Régler sur la validation, tester une seule fois |
| Rééquilibrer **avant** de découper | Des copies d'une même ligne se retrouvent dans le train et le test | Découper d'abord, rééquilibrer ensuite et seulement le train |
| Oublier `random_state` | Résultats différents à chaque exécution | Le fixer partout (42) |
| Charger tout en `float64` | La mémoire explose | Utiliser `float32`, `int8`, `category` |
| Un score proche de 100 % | PaySim est simulé, donc plus « régulier » que la réalité | Le dire dans les limites, ne pas s'en vanter |
| Soldes « après » indisponibles dans la vraie vie | Au moment d'autoriser une transaction, on ne les connaît pas toujours | Le mentionner comme limite |

---

## 16. Livrables, README et CV

### Ce que tu publies sur GitHub

- Le code (`src/`, `notebooks/`, `tests/`), la spec Spec Kit (`specs/`, `.specify/`)
- `README.md`, `requirements.txt`
- 4 à 6 graphiques dans `reports/figures/`
- **Pas** de CSV ni de modèle sauvegardé

### Plan du README

```markdown
# Détection de fraude Mobile Money (PaySim)

## Contexte et objectif
Une phrase sur le besoin métier.

## Les données
PaySim : origine, taille, taux de fraude, colonnes retirées et pourquoi.

## Méthode
Exploration, variables créées, découpage 60/20/20, modèles comparés, choix du seuil.

## Résultats
| Modèle | PR-AUC (validation) | Rappel | Précision |
|---|---|---|---|
Résultat final sur le test avec le seuil choisi, matrice de confusion, courbe précision-rappel.

## Variables les plus importantes
Le graphique et 2 phrases d'interprétation.

## Limites
Données simulées, scores optimistes, soldes "après" pas toujours disponibles, pas de test en production.

## Reproduire le projet
Les commandes : installer, télécharger les données, lancer les notebooks, lancer pytest.

## Méthode de travail
Projet mené avec Spec Kit (voir specs/).
```

### Phrase pour le CV (à écrire seulement une fois le projet terminé, avec tes vrais chiffres)

> Détection de fraude Mobile Money sur 6,3 M de transactions (PaySim) : analyse exploratoire, création de variables, comparaison de modèles (scikit-learn), rappel de [X] % pour [Y] % de précision sur le jeu de test ; démarche Spec Kit.

### Questions d'entretien probables

| Question | Ce que tu dois savoir répondre |
|---|---|
| Pourquoi pas la précision globale ? | Avec 0,13 % de fraudes, répondre « jamais de fraude » donne 99,87 % sans rien trouver |
| Comment as-tu géré le déséquilibre ? | Découpage stratifié, `class_weight="balanced"`, métriques adaptées |
| Pourquoi trois jeux de données ? | Entraîner, régler, puis noter une seule fois sans tricher |
| Comment as-tu choisi le seuil ? | Sur la validation, avec un objectif de rappel de 90 % |
| Qu'est-ce qu'une fuite de données ? | Donner au modèle une information qui contient la réponse ; exemple `isFlaggedFraud` |
| Quelles sont les limites ? | Données simulées, soldes « après », pas de test en conditions réelles |
| Quelles variables ont été les plus utiles ? | Les écarts de soldes et le type de transaction (à confirmer avec ton graphique) |

---

## 17. Bonus : API de scoring

Optionnel (US6). Ça relie le projet à tes compétences en API et en tests de charge.

```python
# api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()
paquet = joblib.load("models/modele_fraude.joblib")
modele, seuil, features = paquet["model"], paquet["seuil"], paquet["features"]


class Transaction(BaseModel):
    heure: int
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    type_transfer: int


@app.post("/score")
def score(t: Transaction):
    d = t.model_dump()
    d["erreur_solde_orig"] = d["oldbalanceOrg"] - d["amount"] - d["newbalanceOrig"]
    d["erreur_solde_dest"] = d["oldbalanceDest"] + d["amount"] - d["newbalanceDest"]
    d["orig_vide_apres"] = int(d["newbalanceOrig"] == 0)
    d["dest_vide_avant"] = int(d["oldbalanceDest"] == 0)
    risque = float(modele.predict_proba(pd.DataFrame([d])[features])[0, 1])
    return {"risque": risque, "alerte": risque >= seuil}
```

Lancement : `uvicorn api.main:app --reload` (après `pip install fastapi uvicorn`). Teste ensuite la route avec Postman, puis mesure la tenue en charge avec Locust. Note les chiffres (requêtes par seconde, temps de réponse) pour le README.

---

## 18. Plan de progression

| Jour | Travail | Résultat attendu |
|---|---|---|
| 1 | Installation, Spec Kit, constitution, spec, clarify | `constitution.md` et `spec.md` écrits |
| 2 | Plan, tâches, analyze ; chargement et exploration (étapes A à C) | Notebook 01 avec 4 graphiques commentés |
| 3 | Variables, découpage, modèle de référence (étapes D à F) | `features.py`, tests, notebook 02 |
| 4 | Modèles, comparaison, seuil (étapes G à H) | Tableau de comparaison, seuil choisi |
| 5 | Test final, importance, README, GitHub (étapes I à L) | Projet publié |

Si tu es novice, prévois **7 à 10 jours** plutôt que 5 : comprendre prend plus de temps que copier du code, et c'est normal.

---

## 19. Check-list finale

- [ ] La constitution, la spec, le plan et les tâches sont dans le dépôt
- [ ] `/speckit.analyze` ne signale plus d'incohérence importante
- [ ] Le CSV n'est pas dans Git
- [ ] `isFlaggedFraud` et les identifiants ne sont pas utilisés comme variables
- [ ] Trois jeux : entraînement, validation, test, avec la même proportion de fraudes
- [ ] Un modèle de référence montre le piège de la précision globale
- [ ] Au moins trois modèles comparés avec les mêmes métriques
- [ ] Seuil choisi sur la validation, test utilisé une seule fois
- [ ] Matrice de confusion et courbe précision-rappel présentes
- [ ] Les limites sont écrites dans le README
- [ ] Les tests pytest passent
- [ ] Le projet se relance de bout en bout avec les mêmes résultats
- [ ] Tu sais **expliquer chaque étape à voix haute** sans regarder le code

---

*Ce guide est un support pédagogique. Les chiffres de PaySim (nombre de lignes, de fraudes, répartition par type) sont à vérifier toi-même à l'étape d'exploration, et les objectifs de rappel et de précision de la spec sont des cibles à ajuster après ton modèle de référence.*
