# Architecture technique — Mini House MLOps

## 1. Vue générale

Le projet **Mini House MLOps** met en œuvre une architecture complète DataOps et MLOps permettant de transformer des données immobilières brutes en un service de prédiction conteneurisé, testé, versionné et supervisé.

L’architecture générale suit le flux suivant :

```text
Source CSV
   |
   v
dlt
Ingestion
   |
   v
DuckDB
Stockage
   |
   v
dbt
Transformation
   |
   v
Tests qualité / Data Contract
   |
   v
Dagster
Orchestration
   |
   v
Scikit-learn
Machine Learning
   |
   v
MLflow
Tracking + Registry
   |
   v
FastAPI
Serving
   |
   v
Docker
Conteneurisation
   |
   v
GitHub Actions
CI/CD
   |
   v
Monitoring & Observabilité
```

---

## 2. Couche Source

La source de données du projet est un fichier CSV :

```text
data/houses.CSV
```

Les principales variables utilisées sont :

```text
surface
rooms
age
distance_city
price
```

Les quatre premières variables servent de features pour le modèle de Machine Learning.

La variable :

```text
price
```

représente la cible à prédire.

---

## 3. Ingestion avec dlt

La première étape du pipeline consiste à ingérer automatiquement les données.

L’outil utilisé est :

```text
dlt
```

Son rôle est de :

* lire les données sources ;
* automatiser l’ingestion ;
* charger les données dans DuckDB ;
* rendre le processus reproductible ;
* limiter les manipulations manuelles.

Le flux est :

```text
houses.CSV
   |
   v
dlt
   |
   v
DuckDB
```

---

## 4. Stockage avec DuckDB

DuckDB constitue la couche de stockage analytique du projet.

La base utilisée est :

```text
warehouse/house_prices.duckdb
```

Une première couche contient les données brutes ingérées.

Le pipeline évolue ensuite vers des tables transformées utilisables par les étapes suivantes.

Architecture logique :

```text
DuckDB
|
├── raw_data
|
├── staging
|
└── analytics
```

La table finale utilisée pour le Machine Learning est :

```text
analytics.ml_houses
```

---

## 5. Transformation avec dbt

dbt assure la transformation des données.

Le pipeline de transformation suit principalement :

```text
raw_data.houses
        |
        v
staging.stg_houses
        |
        v
analytics.ml_houses
```

### Couche staging

La couche staging permet de nettoyer, renommer, filtrer ou préparer les données brutes.

Modèle principal :

```text
stg_houses
```

### Couche analytics

La couche analytics contient les données prêtes pour les usages analytiques et Machine Learning.

Modèle principal :

```text
ml_houses
```

Cette séparation permet d’éviter que le modèle ML travaille directement sur les données brutes.

---

## 6. Qualité des données

Les transformations sont accompagnées de contrôles de qualité.

Le projet inclut notamment :

* contrôle des valeurs nulles ;
* contrôle de validité ;
* tests automatisés dbt ;
* vérification de freshness ;
* Data Contract ;
* documentation des données.

Pendant le développement, un test de qualité a permis de détecter une valeur invalide :

```text
-55
```

Cette anomalie a démontré l’intérêt des contrôles automatisés avant l’utilisation des données par le modèle.

La logique est donc :

```text
Données
   |
   v
Transformation
   |
   v
Tests qualité
   |
   +---- Erreur ----> Correction
   |
   v
Données validées
```

---

## 7. Orchestration avec Dagster

Dagster orchestre les différentes étapes DataOps.

Il permet de :

* ordonner les traitements ;
* gérer les dépendances ;
* consulter les logs ;
* visualiser l’état des exécutions ;
* identifier les erreurs ;
* relancer les traitements.

Le pipeline logique est :

```text
Ingestion
   |
   v
Freshness
   |
   v
dbt run
   |
   v
dbt test
```

Dagster joue ainsi le rôle de coordinateur entre plusieurs composants indépendants.

---

## 8. Couche Machine Learning

Les données utilisées par le modèle proviennent de :

```text
analytics.ml_houses
```

Le script principal d’entraînement est :

```text
ml/train.py
```

### Features

```text
surface
rooms
age
distance_city
```

### Target

```text
price
```

Deux algorithmes ont été comparés :

```text
LinearRegression
RandomForestRegressor
```

Le dataset est séparé en :

```text
80 % entraînement
20 % test
```

avec :

```text
random_state = 42
```

---

## 9. Évaluation des modèles

Les modèles sont évalués avec :

```text
MAE
RMSE
R²
```

Une baseline est également utilisée.

Le modèle final n’est donc pas sélectionné arbitrairement.

Les différentes expériences sont comparées à partir de leurs performances sur le jeu de test.

Le critère principal utilisé pour sélectionner le meilleur modèle est :

```text
test_mae
```

La meilleure run correspond à celle ayant :

```text
test_mae minimale
```

---

## 10. MLflow Tracking

MLflow assure le suivi des expériences Machine Learning.

Le serveur MLflow est exposé sur :

```text
http://localhost:5000
```

L’expérience utilisée est :

```text
house_price_prediction
```

Pour chaque modèle, MLflow conserve notamment :

### Paramètres

Exemples :

```text
model_type
test_size
random_state
n_estimators
```

### Métriques

```text
train_mae
train_rmse
train_r2

test_mae
test_rmse
test_r2

baseline_mae
```

### Artefacts

Le modèle entraîné est également enregistré comme artefact MLflow.

---

## 11. MLflow Model Registry

Le script :

```text
ml/register_best_model.py
```

recherche automatiquement la meilleure run terminée selon :

```text
metrics.test_mae ASC
```

Le modèle sélectionné est enregistré sous le nom :

```text
HousePriceModel
```

Un alias est attribué à la version validée :

```text
champion
```

L’URI logique utilisée par l’application devient donc :

```text
models:/HousePriceModel@champion
```

Cette architecture découple le service FastAPI d’une version numérique particulière du modèle.

Ainsi, une nouvelle version peut devenir `champion` sans modification du code de l’API.

---

## 12. Serving avec FastAPI

Le service ML est implémenté dans :

```text
api/main.py
```

FastAPI charge le champion depuis MLflow lors du démarrage de l’application.

Le service expose plusieurs endpoints.

### Disponibilité

```text
GET /health
```

### Prédiction

```text
POST /predict
```

### Monitoring applicatif

```text
GET /metrics
```

### Métriques Machine Learning

```text
GET /ml-metrics
```

### Dérive des données

```text
GET /drift
```

### Documentation Swagger

```text
GET /docs
```

---

## 13. Validation des entrées

Les entrées du endpoint `/predict` sont validées avec Pydantic.

Le modèle attendu contient :

```text
surface > 0
rooms > 0
age >= 0
distance_city >= 0
```

Une donnée invalide est rejetée automatiquement avec :

```text
HTTP 422
```

Cela empêche d’envoyer au modèle des valeurs ne respectant pas le contrat de l’API.

---

## 14. Tests de l’API

Les tests sont stockés dans :

```text
tests/test_api.py
```

Ils utilisent :

```text
pytest
FastAPI TestClient
monkeypatch
```

Un :

```text
FakeModel
```

remplace le véritable modèle MLflow pendant les tests.

Cela rend les tests :

* rapides ;
* reproductibles ;
* indépendants d’un serveur MLflow réel.

Un faux client MLflow est également utilisé pour tester `/ml-metrics`.

La suite actuelle contient :

```text
9 tests
```

---

## 15. Conteneurisation Docker

L’API est empaquetée dans une image Docker.

Le Dockerfile utilise :

```text
python:3.10-slim
```

La construction est réalisée avec :

```bash
docker build -t mini-house-api:1.0 .
```

Le conteneur expose :

```text
8000
```

Le mapping utilisé est :

```text
Windows 8000
      |
      v
Docker 8000
```

---

## 16. Communication Docker vers MLflow

MLflow reste exécuté sur la machine hôte.

À l’intérieur d’un conteneur :

```text
127.0.0.1
```

désigne le conteneur lui-même.

L’API utilise donc :

```text
host.docker.internal
```

pour joindre MLflow sur la machine Windows.

La variable d’environnement est :

```text
MLFLOW_TRACKING_URI=http://host.docker.internal:5000
```

Architecture :

```text
Docker Container
FastAPI :8000
      |
      |
      v
host.docker.internal:5000
      |
      v
MLflow sur Windows
      |
      v
HousePriceModel@champion
```

---

## 17. Docker HEALTHCHECK

L’image contient un contrôle de santé Docker.

Il interroge :

```text
http://localhost:8000/health
```

Docker peut ainsi déterminer si le service est :

```text
starting
healthy
unhealthy
```

La commande :

```bash
docker ps
```

permet de vérifier l’état de santé du conteneur.

---

## 18. Docker Layers et cache

Le Dockerfile est organisé de manière à tirer parti du système de cache.

Les dépendances sont copiées avant le code :

```text
COPY requirements-api.txt .
RUN pip install ...
COPY api ./api
```

Ainsi, lorsqu’un fichier Python de l’API est modifié sans modifier les dépendances, Docker peut réutiliser les couches d’installation précédentes.

Cela réduit fortement le temps de reconstruction.

---

## 19. CI/CD avec GitHub Actions

Le pipeline CI est défini dans :

```text
.github/workflows/ci.yml
```

Il est exécuté lors d’un :

```text
push
```

ou d’une :

```text
pull_request
```

Le processus est :

```text
Git Push
   |
   v
GitHub Actions
   |
   v
Checkout
   |
   v
Python 3.10
   |
   v
Installation dépendances
   |
   v
Vérification syntaxique
   |
   v
Pytest
   |
   v
Docker Build
   |
   v
CI Success
```

La vérification syntaxique utilise :

```bash
python -m compileall api tests
```

Les tests utilisent :

```bash
python -m pytest -q
```

Le build CI utilise :

```bash
docker build -t mini-house-api:ci .
```

---

## 20. Monitoring de disponibilité

La disponibilité est contrôlée à deux niveaux.

### Niveau API

```text
GET /health
```

### Niveau Docker

```text
HEALTHCHECK
```

Cette double vérification permet de savoir à la fois si le processus fonctionne et si l’API répond correctement.

---

## 21. Monitoring applicatif

Le endpoint :

```text
GET /metrics
```

expose notamment :

```text
total_requests
successful_requests
client_errors
server_errors
last_response_time_ms
average_response_time_ms
```

Le middleware FastAPI mesure chaque requête.

Les erreurs HTTP 4xx sont comptabilisées comme erreurs client.

Les erreurs 5xx sont considérées comme erreurs serveur.

---

## 22. Monitoring des métriques ML

Le endpoint :

```text
GET /ml-metrics
```

interroge MLflow Model Registry.

Le processus est :

```text
HousePriceModel@champion
        |
        v
Model Version
        |
        v
Run ID
        |
        v
MLflow Run
        |
        v
Metrics
```

L’API peut ainsi retourner les performances du modèle réellement déployé.

Cela évite de coder les valeurs de métriques en dur dans l’application.

---

## 23. Monitoring de dérive

Le projet met en œuvre une détection simple de dérive des données.

Les statistiques de référence sont générées depuis :

```text
analytics.ml_houses
```

par le script :

```text
ml/create_reference_stats.py
```

Le fichier produit est :

```text
api/reference_stats.json
```

Les statistiques de référence comprennent :

```text
mean
std
min
max
```

pour chaque feature.

Les moyennes de référence sont :

```text
surface       = 105.50
rooms         = 3.40
age           = 5.95
distance_city = 4.86
```

Le endpoint :

```text
GET /drift
```

compare ces valeurs avec les moyennes calculées à partir des requêtes reçues en production.

Le seuil utilisé est :

```text
20 %
```

Si une feature dépasse ce seuil d’écart relatif :

```text
drift_detected = true
```

Si au moins une feature présente une dérive :

```text
overall_drift = true
```

---

## 24. Architecture de monitoring

```text
                 FastAPI
                    |
       +------------+------------+
       |            |            |
       v            v            v
    /health      /metrics     /predict
       |            |            |
       |            |            |
       |            |            +------+
       |            |                   |
       |            v                   v
       |      API Monitoring      Production Data
       |                                |
       v                                v
Docker HEALTHCHECK                   /drift

                    +
                    |
                    v

              /ml-metrics
                    |
                    v
                  MLflow
                    |
                    v
            Champion Metrics
```

---

## 25. Séparation des responsabilités

L’architecture respecte une séparation claire entre les composants.

### dlt

Responsable de l’ingestion.

### DuckDB

Responsable du stockage analytique.

### dbt

Responsable des transformations et de la qualité.

### Dagster

Responsable de l’orchestration.

### Scikit-learn

Responsable du Machine Learning.

### MLflow

Responsable du tracking et du registry.

### FastAPI

Responsable du serving.

### Pytest

Responsable des tests applicatifs.

### Docker

Responsable de la conteneurisation.

### GitHub Actions

Responsable de la CI/CD.

### Monitoring

Responsable de l’observabilité du service et du modèle.

---

## 26. Principes MLOps illustrés

Cette architecture illustre plusieurs principes importants :

* reproductibilité ;
* automatisation ;
* traçabilité ;
* tests automatisés ;
* versionnement ;
* séparation des responsabilités ;
* qualité des données ;
* model registry ;
* déploiement reproductible ;
* CI/CD ;
* monitoring ;
* observabilité.

---

## 27. Architecture finale résumée

```text
                       DATAOPS
                         |
                         v
houses.CSV → dlt → DuckDB → dbt
                         |
                         v
                  Data Quality
                         |
                         v
                      Dagster
                         |
                         v
                       MLOPS
                         |
                         v
                Scikit-learn
                         |
                         v
                       MLflow
               Tracking + Registry
                         |
                         v
             HousePriceModel@champion
                         |
                         v
                       FastAPI
                  /predict /health
                         |
                         v
                       Docker
                         |
                         v
                  GitHub Actions
                         |
                         v
                     Monitoring
               API + ML + Data Drift
```

Cette architecture permet donc de couvrir le cycle complet allant de la donnée brute jusqu’à un service Machine Learning conteneurisé, testé et supervisé.
