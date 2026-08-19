# Guide d'utilisation — Mini House MLOps

## 1. Objectif du guide

Ce document explique comment utiliser concrètement le projet **Mini House MLOps — Observatoire intelligent des prix immobiliers** après son installation.

Le projet met en œuvre le cycle suivant :

```text
Données
   ↓
Ingestion
   ↓
Transformation
   ↓
Qualité
   ↓
Orchestration
   ↓
Machine Learning
   ↓
MLflow
   ↓
Model Registry
   ↓
FastAPI
   ↓
Docker
   ↓
CI/CD
   ↓
Monitoring
```

Ce guide présente notamment comment :

* préparer l’environnement ;
* exécuter le pipeline DataOps ;
* entraîner les modèles ;
* consulter les expériences MLflow ;
* enregistrer le meilleur modèle ;
* utiliser le modèle `champion` ;
* lancer l’API FastAPI ;
* effectuer une prédiction ;
* exécuter les tests ;
* construire et lancer le conteneur Docker ;
* consulter les métriques ;
* observer la dérive ;
* déclencher la CI GitHub Actions.

---

# 2. Se placer à la racine du projet

Toutes les commandes principales doivent être exécutées depuis la racine :

```text
mini-house-mlops/
```

Dans l’environnement utilisé pendant le développement :

```cmd
cd /d "D:\cours master\s2\MLops\comprendre projet\mini-house-mlops"
```

Le chemin exact dépend naturellement de la machine utilisée.

---

# 3. Activer l'environnement virtuel

Sous Windows CMD :

```cmd
.venv\Scripts\activate
```

Le terminal doit ensuite afficher :

```text
(.venv)
```

Exemple :

```text
(.venv) D:\...\mini-house-mlops>
```

Cette étape est importante afin d’utiliser les versions de Python et des dépendances installées pour le projet.

---

# 4. Vérifier l'état du projet Git

Avant de commencer une session de travail :

```bash
git status
```

Pour vérifier la branche :

```bash
git branch --show-current
```

La branche principale utilisée dans le projet est :

```text
main
```

Pour vérifier le dépôt distant :

```bash
git remote -v
```

---

# 5. Source de données

La source de données utilisée est :

```text
data/houses.CSV
```

Elle contient notamment :

```text
surface
rooms
age
distance_city
price
```

Les quatre premières colonnes servent d’entrées au modèle.

La colonne :

```text
price
```

est la variable cible.

---

# 6. Pipeline DataOps

Le pipeline DataOps suit la chaîne suivante :

```text
houses.CSV
     ↓
    dlt
     ↓
   DuckDB
     ↓
    dbt
     ↓
Tests qualité
     ↓
  Dagster
```

L’objectif est de ne jamais entraîner directement le modèle à partir du fichier brut sans passer par les différentes étapes de préparation et de qualité.

---

# 7. Ingestion des données

La première étape consiste à ingérer les données sources avec **dlt**.

Le code d’ingestion se trouve dans :

```text
ingestion/
```

Cette étape charge les données dans DuckDB.

La couche brute utilisée dans l’architecture est :

```text
raw_data.houses
```

Après ingestion, vérifier que la base existe :

```text
warehouse/house_prices.duckdb
```

---

# 8. Transformation avec dbt

Le projet dbt se trouve dans :

```text
dbt_project/
```

L’objectif est de transformer progressivement :

```text
raw_data.houses
        ↓
staging.stg_houses
        ↓
analytics.ml_houses
```

La table finale :

```text
analytics.ml_houses
```

est celle utilisée par le Machine Learning.

Depuis l’environnement dbt correctement configuré, les opérations principales sont :

```bash
dbt run
```

pour construire les modèles, puis :

```bash
dbt test
```

pour exécuter les contrôles de qualité.

Lorsque la freshness est configurée :

```bash
dbt source freshness
```

permet également de contrôler la fraîcheur de la source.

---

# 9. Qualité des données

Les tests de qualité doivent être exécutés avant l’entraînement du modèle.

Ils permettent notamment de détecter :

* valeurs nulles ;
* valeurs invalides ;
* problèmes de cohérence ;
* erreurs de structure ;
* problèmes de fraîcheur.

Pendant le développement, les tests ont notamment détecté une valeur invalide :

```text
-55
```

Ce type d’erreur doit être corrigé avant de considérer le pipeline de données comme valide.

La logique recommandée est :

```text
dbt run
   ↓
dbt test
   ↓
Tests OK ?
   │
   ├── NON → corriger
   │
   └── OUI
        ↓
      ML
```

---

# 10. Orchestration avec Dagster

Dagster permet d’orchestrer les différentes étapes du pipeline.

Le code correspondant se trouve dans :

```text
orchestration/
```

Le pipeline permet notamment d’enchaîner :

```text
Ingestion
   ↓
Freshness
   ↓
Transformations dbt
   ↓
Tests dbt
```

L’interface Dagster permet de :

* lancer les jobs ;
* visualiser les étapes ;
* consulter les logs ;
* identifier une étape en erreur ;
* relancer une exécution.

Avant de passer au Machine Learning, vérifier que le pipeline Dagster se termine correctement.

---

# 11. Vérifier les données ML

Le script d’entraînement utilise :

```text
warehouse/house_prices.duckdb
```

et lit :

```text
analytics.ml_houses
```

Les colonnes utilisées sont :

```text
surface
rooms
age
distance_city
price
```

Les features sont :

```text
X = [
    surface,
    rooms,
    age,
    distance_city
]
```

et la target est :

```text
y = price
```

---

# 12. Démarrer MLflow

Avant d’entraîner ou d’utiliser les modèles enregistrés, démarrer le serveur MLflow.

Depuis la racine du projet :

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000
```

Laisser ce terminal ouvert.

Puis ouvrir dans le navigateur :

```text
http://localhost:5000
```

Ne pas utiliser directement :

```text
http://0.0.0.0:5000
```

car `0.0.0.0` correspond à une adresse d’écoute du serveur.

---

# 13. Entraîner les modèles

Le script principal est :

```text
ml/train.py
```

Exécution :

```bash
python ml/train.py
```

Le script entraîne deux modèles :

```text
LinearRegression
RandomForestRegressor
```

avec une séparation :

```text
80 % train
20 % test
```

et :

```text
random_state = 42
```

---

# 14. Métriques calculées pendant l'entraînement

Pour chaque modèle, le projet calcule :

```text
MAE
RMSE
R²
```

sur les données d’entraînement et les données de test.

Les métriques enregistrées dans MLflow sont :

```text
train_mae
train_rmse
train_r2

test_mae
test_rmse
test_r2

baseline_mae
```

---

# 15. Résultats obtenus pendant le projet

## Linear Regression — Train

```text
MAE  : 10 093.76
RMSE : 13 267.19
R²   : 0.99897
```

## Linear Regression — Test

```text
MAE  : 47 891.96
RMSE : 58 847.74
R²   : 0.98933
```

## Random Forest — Train

```text
MAE  : 31 343.75
RMSE : 47 900.88
R²   : 0.98660
```

## Random Forest — Test

```text
MAE  : 134 975.00
RMSE : 138 081.60
R²   : 0.94127
```

Baseline :

```text
MAE = 562 500
```

La régression linéaire a donc obtenu la meilleure MAE de test parmi les modèles évalués.

---

# 16. Consulter les expériences dans MLflow

Après l’entraînement, ouvrir :

```text
http://localhost:5000
```

Puis sélectionner l’expérience :

```text
house_price_prediction
```

Les runs disponibles comprennent notamment :

```text
linear_regression
random_forest
```

Pour chaque run, MLflow permet d’examiner :

* paramètres ;
* métriques ;
* artefacts ;
* modèle sauvegardé.

---

# 17. Enregistrer le meilleur modèle

Le script utilisé est :

```text
ml/register_best_model.py
```

Lancer :

```bash
python ml/register_best_model.py
```

Le script recherche la meilleure run selon :

```text
metrics.test_mae ASC
```

c’est-à-dire la plus petite MAE sur le jeu de test.

---

# 18. Model Registry

Le modèle sélectionné est enregistré sous :

```text
HousePriceModel
```

Le script attribue l’alias :

```text
champion
```

L’URI utilisée ensuite est :

```text
models:/HousePriceModel@champion
```

L’intérêt de cet alias est de ne pas coder une version numérique dans l’API.

Par exemple :

```text
Version 1 → champion
```

peut ensuite devenir :

```text
Version 2 → champion
```

sans modifier :

```text
api/main.py
```

---

# 19. Vérifier le modèle du Registry

Le projet contient également :

```text
ml/predict_from_registry.py
```

Ce script permet de vérifier qu’un modèle enregistré dans MLflow Model Registry peut être chargé et utilisé.

Il peut être utilisé comme contrôle complémentaire avant de démarrer FastAPI.

---

# 20. Générer les statistiques de référence du monitoring

Avant d’utiliser le monitoring de dérive, générer :

```text
api/reference_stats.json
```

avec :

```bash
python ml/create_reference_stats.py
```

Le script utilise directement :

```text
analytics.ml_houses
```

comme dataset de référence.

---

# 21. Statistiques de référence obtenues

Le dataset de référence utilisé pendant le projet contient :

```text
20 observations
```

Les moyennes sont :

| Feature       | Moyenne |
| ------------- | ------: |
| surface       |  105.50 |
| rooms         |    3.40 |
| age           |    5.95 |
| distance_city |    4.86 |

Les statistiques sauvegardées incluent également :

```text
std
min
max
```

---

# 22. Exécuter les tests

Avant de lancer l’API ou de faire un commit :

```bash
python -m pytest -v
```

Pour une sortie plus compacte :

```bash
python -m pytest -q
```

La commande à privilégier dans ce projet est :

```bash
python -m pytest
```

plutôt que l’exécution directe de :

```bash
pytest
```

car l’utilisation directe de `pytest` a provoqué sous Windows :

```text
ModuleNotFoundError: No module named 'api'
```

---

# 23. Tests disponibles

La suite actuelle contient :

```text
9 tests
```

Résultat attendu :

```text
9 passed
```

Ils vérifient notamment :

```text
GET /health
POST /predict valide
POST /predict surface négative
POST /predict rooms = 0
POST /predict age négatif
POST /predict champ manquant
GET /metrics
GET /ml-metrics
GET /drift
```

---

# 24. Tests indépendants de MLflow

Les tests API utilisent un :

```text
FakeModel
```

afin d’éviter le chargement réel de :

```text
HousePriceModel@champion
```

pendant les tests.

Le endpoint `/ml-metrics` utilise également un faux client MLflow dans les tests.

Cette architecture permet à :

```text
GitHub Actions
```

d’exécuter les tests sans avoir besoin de démarrer un serveur MLflow réel.

---

# 25. Lancer FastAPI directement

Avec MLflow actif, démarrer FastAPI :

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

L’API charge automatiquement :

```text
models:/HousePriceModel@champion
```

pendant son démarrage.

---

# 26. Accéder à Swagger

Ouvrir :

```text
http://localhost:8000/docs
```

Swagger permet de tester facilement tous les endpoints.

Les endpoints principaux sont :

```text
GET  /health
POST /predict
GET  /metrics
GET  /ml-metrics
GET  /drift
```

---

# 27. Vérifier l'état de l'API

Ouvrir :

```text
http://localhost:8000/health
```

Résultat attendu :

```json
{
  "status": "ok",
  "model": "models:/HousePriceModel@champion"
}
```

Ce endpoint indique que le service répond.

---

# 28. Effectuer une prédiction

Dans Swagger :

```text
POST /predict
```

Cliquer sur :

```text
Try it out
```

Puis utiliser par exemple :

```json
{
  "surface": 120,
  "rooms": 4,
  "age": 10,
  "distance_city": 5
}
```

Puis cliquer sur :

```text
Execute
```

---

# 29. Réponse de prédiction

Une réponse valide utilise :

```text
HTTP 200
```

et contient :

```json
{
  "predicted_price": 1234567.89,
  "model": "HousePriceModel@champion"
}
```

La valeur de `predicted_price` dépend naturellement du modèle et des caractéristiques du logement.

---

# 30. Validation des entrées

Les contraintes de l’API sont :

```text
surface > 0
rooms > 0
age >= 0
distance_city >= 0
```

Exemple invalide :

```json
{
  "surface": -20,
  "rooms": 4,
  "age": 10,
  "distance_city": 5
}
```

Résultat attendu :

```text
HTTP 422
```

Ce résultat est normal.

Il signifie que FastAPI/Pydantic a rejeté les données avant de les envoyer au modèle.

---

# 31. Monitoring de l'API

Ouvrir :

```text
http://localhost:8000/metrics
```

Le endpoint retourne notamment :

```text
total_requests
successful_requests
client_errors
server_errors
last_response_time_ms
average_response_time_ms
```

---

# 32. Générer de l'activité pour le monitoring

Faire plusieurs appels :

```text
GET /health
```

puis plusieurs :

```text
POST /predict
```

et recharger :

```text
GET /metrics
```

Le compteur :

```text
total_requests
```

doit augmenter.

Une requête valide augmente :

```text
successful_requests
```

Une requête produisant `422` augmente :

```text
client_errors
```

---

# 33. Monitoring des métriques du modèle

Ouvrir :

```text
http://localhost:8000/ml-metrics
```

L’API interroge MLflow afin de retrouver :

```text
HousePriceModel@champion
```

puis la run associée.

Elle retourne notamment :

```text
train_mae
train_rmse
train_r2
test_mae
test_rmse
test_r2
baseline_mae
```

Ainsi, les performances présentées correspondent au modèle réellement déployé.

---

# 34. Monitoring de la dérive

Ouvrir :

```text
http://localhost:8000/drift
```

Avant toute prédiction, le endpoint doit indiquer :

```text
waiting_for_predictions
```

avec :

```text
prediction_count = 0
```

---

# 35. Tester un cas sans dérive importante

Les valeurs de référence sont proches de :

```text
surface       = 105.50
rooms         = 3.40
age           = 5.95
distance_city = 4.86
```

Un exemple de requête proche de cette distribution est :

```json
{
  "surface": 105.5,
  "rooms": 3,
  "age": 6,
  "distance_city": 4.86
}
```

Après quelques requêtes comparables, consulter :

```text
GET /drift
```

Le résultat doit normalement conserver :

```text
overall_drift = false
```

tant que les moyennes de production restent proches de la référence.

---

# 36. Tester volontairement une dérive

Pour démontrer le fonctionnement du monitoring, il est possible d’envoyer des valeurs nettement différentes.

Exemple :

```json
{
  "surface": 200,
  "rooms": 6,
  "age": 18,
  "distance_city": 9
}
```

Puis consulter :

```text
GET /drift
```

Une ou plusieurs features peuvent alors indiquer :

```text
drift_detected = true
```

et :

```text
overall_drift = true
```

---

# 37. Méthode de dérive utilisée

Le monitoring compare :

```text
moyenne production
```

avec :

```text
moyenne de référence
```

et calcule un écart relatif.

Le seuil utilisé est :

```text
20 %
```

Cette approche est volontairement simple.

Elle correspond à une démonstration pédagogique de la dérive plutôt qu’à une solution statistique de production avancée.

---

# 38. Lancer l'API avec Docker

Docker Desktop doit être actif.

Vérification :

```bash
docker info
```

Puis construire l’image :

```bash
docker build -t mini-house-api:1.0 .
```

---

# 39. Vérifier l'image Docker

```bash
docker images mini-house-api
```

L’image doit apparaître sous :

```text
mini-house-api:1.0
```

---

# 40. MLflow et Docker

Lorsque FastAPI s’exécute dans Docker et MLflow directement sur Windows, utiliser :

```text
host.docker.internal
```

et non :

```text
127.0.0.1
```

L’adresse utilisée par le conteneur est :

```text
http://host.docker.internal:5000
```

---

# 41. Lancer le conteneur Docker

Avec MLflow actif :

```bash
docker run -d --name mini-house-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 mini-house-api:1.0
```

Le mode :

```text
-d
```

permet au conteneur de fonctionner en arrière-plan.

---

# 42. Vérifier le HEALTHCHECK Docker

Exécuter :

```bash
docker ps
```

Après le démarrage, l’état doit devenir :

```text
healthy
```

Docker vérifie automatiquement :

```text
http://localhost:8000/health
```

à l’intérieur du conteneur.

---

# 43. Consulter les logs

```bash
docker logs mini-house-api
```

Les logs permettent notamment de vérifier :

```text
Chargement du modèle
models:/HousePriceModel@champion
Application startup complete
```

---

# 44. Tester l'API Dockerisée

Les mêmes URLs restent accessibles depuis Windows :

```text
http://localhost:8000/health
http://localhost:8000/docs
http://localhost:8000/metrics
http://localhost:8000/ml-metrics
http://localhost:8000/drift
```

Le endpoint :

```text
POST /predict
```

reste disponible depuis Swagger.

---

# 45. Arrêter le conteneur

```bash
docker stop mini-house-api
```

---

# 46. Redémarrer le conteneur

```bash
docker start mini-house-api
```

---

# 47. Supprimer le conteneur

```bash
docker stop mini-house-api
docker rm mini-house-api
```

L’image reste disponible.

---

# 48. Rebuild après une modification

Après une modification de :

```text
api/main.py
```

il faut reconstruire l’image.

Procédure :

```bash
docker stop mini-house-api
docker rm mini-house-api
docker build -t mini-house-api:1.0 .
```

Puis :

```bash
docker run -d --name mini-house-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 mini-house-api:1.0
```

---

# 49. Cache Docker

Lors d’un rebuild, Docker peut afficher :

```text
CACHED
```

Cela signifie qu’une couche précédente n’a pas changé et peut être réutilisée.

Le Dockerfile copie d’abord :

```text
requirements-api.txt
```

puis installe les dépendances, avant de copier :

```text
api/
```

Cette organisation évite de réinstaller toutes les dépendances Python après chaque petite modification du code API.

---

# 50. CI/CD avec GitHub Actions

Le workflow se trouve dans :

```text
.github/workflows/ci.yml
```

Il est déclenché automatiquement par :

```text
git push
```

ou par une Pull Request.

---

# 51. Contenu du pipeline CI

Le pipeline exécute :

```text
Checkout du code
       ↓
Python 3.10
       ↓
Installation des dépendances
       ↓
Vérification de la syntaxe
       ↓
Tests Pytest
       ↓
Build Docker
```

La vérification syntaxique utilise :

```bash
python -m compileall api tests
```

Les tests utilisent :

```bash
python -m pytest -q
```

Le build utilise :

```bash
docker build -t mini-house-api:ci .
```

---

# 52. Déclencher la CI

Après modification :

```bash
git status
```

Ajouter les fichiers concernés :

```bash
git add <fichiers>
```

Créer un commit :

```bash
git commit -m "Description de la modification"
```

Puis :

```bash
git push origin main
```

Le `push` déclenche automatiquement GitHub Actions.

---

# 53. Vérifier GitHub Actions

Sur GitHub :

```text
Dépôt
→ Actions
→ CI - Mini House MLOps
```

Le workflow doit terminer avec une coche verte.

Les étapes principales doivent être validées :

```text
Recuperer le code             ✅
Installer Python 3.10         ✅
Installer les dependances     ✅
Verifier la syntaxe Python    ✅
Executer les tests            ✅
Construire l image Docker     ✅
```

---

# 54. Cycle de développement recommandé

Pour une modification de l’API :

```text
Modifier api/main.py
        ↓
python -m pytest -q
        ↓
9 passed
        ↓
Rebuild Docker
        ↓
Tester localement
        ↓
git add
        ↓
git commit
        ↓
git push
        ↓
GitHub Actions
        ↓
CI verte
```

---

# 55. Cycle Machine Learning recommandé

Pour entraîner une nouvelle version :

```text
Pipeline DataOps valide
        ↓
analytics.ml_houses
        ↓
python ml/train.py
        ↓
MLflow Experiments
        ↓
Comparer les métriques
        ↓
python ml/register_best_model.py
        ↓
Nouvelle version du Registry
        ↓
Alias champion
        ↓
FastAPI charge le champion
```

---

# 56. Cycle Data Drift recommandé

Lorsque les données d’entraînement évoluent :

```text
Nouvelles données
      ↓
Pipeline DataOps
      ↓
Nouvelle analytics.ml_houses
      ↓
Réentraînement éventuel
      ↓
python ml/create_reference_stats.py
      ↓
Nouvelles statistiques de référence
      ↓
Rebuild Docker
```

Il est important de régénérer :

```text
api/reference_stats.json
```

si la distribution du dataset de référence change.

---

# 57. Scénario complet de démonstration

Pour une démonstration du projet, utiliser par exemple cet ordre :

## Étape 1

Montrer :

```text
data/houses.CSV
```

## Étape 2

Présenter le pipeline :

```text
dlt → DuckDB → dbt → Dagster
```

## Étape 3

Montrer :

```text
analytics.ml_houses
```

## Étape 4

Ouvrir MLflow :

```text
http://localhost:5000
```

## Étape 5

Présenter les runs :

```text
linear_regression
random_forest
```

## Étape 6

Présenter :

```text
HousePriceModel@champion
```

dans Model Registry.

## Étape 7

Montrer Docker :

```bash
docker ps
```

avec :

```text
healthy
```

## Étape 8

Ouvrir :

```text
http://localhost:8000/docs
```

## Étape 9

Tester :

```text
POST /predict
```

## Étape 10

Montrer :

```text
GET /health
GET /metrics
GET /ml-metrics
GET /drift
```

## Étape 11

Montrer GitHub Actions avec le pipeline vert.

---

# 58. Scénario de prédiction conseillé pour la démonstration

Dans Swagger :

```json
{
  "surface": 120,
  "rooms": 4,
  "age": 10,
  "distance_city": 5
}
```

Résultat :

```text
HTTP 200
```

avec le prix prédit.

Ensuite montrer une erreur de validation :

```json
{
  "surface": -20,
  "rooms": 4,
  "age": 10,
  "distance_city": 5
}
```

Résultat :

```text
HTTP 422
```

Cela permet de démontrer le contrat d’entrée de l’API.

---

# 59. Scénario Monitoring conseillé pour la démonstration

Présenter successivement :

```text
/health
```

pour la disponibilité.

Puis :

```text
/metrics
```

pour :

* nombre de requêtes ;
* succès ;
* erreurs ;
* temps de réponse.

Puis :

```text
/ml-metrics
```

pour les performances du champion.

Enfin :

```text
/drift
```

pour la surveillance des données entrantes.

---

# 60. Commandes essentielles à retenir

## Tests

```bash
python -m pytest -q
```

## Entraînement

```bash
python ml/train.py
```

## Enregistrement du meilleur modèle

```bash
python ml/register_best_model.py
```

## Statistiques de drift

```bash
python ml/create_reference_stats.py
```

## MLflow

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000
```

## FastAPI

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

## Docker build

```bash
docker build -t mini-house-api:1.0 .
```

## Docker run

```bash
docker run -d --name mini-house-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 mini-house-api:1.0
```

## Docker status

```bash
docker ps
```

## Docker logs

```bash
docker logs mini-house-api
```

## Git

```bash
git status
git add <fichiers>
git commit -m "message"
git push origin main
```

---

# 61. URLs essentielles

| Fonction        | URL                                |
| --------------- | ---------------------------------- |
| MLflow          | `http://localhost:5000`            |
| Swagger FastAPI | `http://localhost:8000/docs`       |
| Health          | `http://localhost:8000/health`     |
| Monitoring API  | `http://localhost:8000/metrics`    |
| Métriques ML    | `http://localhost:8000/ml-metrics` |
| Data Drift      | `http://localhost:8000/drift`      |

---

# 62. Bonnes pratiques d'utilisation

Avant un `git push` :

```text
1. Vérifier le code
2. Exécuter les tests
3. Vérifier 9 passed
4. Tester Docker si le serving a changé
5. Vérifier git status
6. Committer uniquement les fichiers nécessaires
7. Push
8. Vérifier GitHub Actions
```

Avant un changement de modèle :

```text
1. Vérifier la qualité des données
2. Entraîner
3. Comparer les métriques
4. Enregistrer la meilleure version
5. Vérifier l'alias champion
6. Tester l'API
7. Vérifier les métriques ML
```

---

# 63. Limites à prendre en compte

Le dataset utilisé dans ce mini-projet contient seulement :

```text
20 observations
```

Les résultats de Machine Learning sont donc principalement pédagogiques.

Les performances obtenues ne garantissent pas les mêmes performances sur un véritable marché immobilier.

Le monitoring de dérive repose également sur une méthode simple basée sur les moyennes et un seuil heuristique de :

```text
20 %
```

---

# 64. Résumé du fonctionnement

L’utilisation normale du système peut être résumée par :

```text
DataOps
   ↓
Données validées
   ↓
Machine Learning
   ↓
MLflow
   ↓
Champion
   ↓
FastAPI
   ↓
Docker
   ↓
Utilisateur
   ↓
Prédiction
   ↓
Monitoring
```

Le projet permet ainsi de démontrer l’ensemble du cycle de vie d’un modèle de Machine Learning, depuis la donnée brute jusqu’à son utilisation via un service conteneurisé et supervisé.
