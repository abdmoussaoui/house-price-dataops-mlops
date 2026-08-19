# Mini House MLOps — Observatoire intelligent des prix immobiliers

## 1. Présentation du projet

**Mini House MLOps** est un projet pédagogique réalisé dans le cadre du module **MLOps & DataOps**.

L’objectif est de construire une chaîne DataOps/MLOps complète permettant de partir de données immobilières brutes jusqu’à l’exposition d’un modèle de Machine Learning via une API conteneurisée et supervisée.

Le cas d’usage consiste à **estimer le prix d’un logement** à partir de plusieurs caractéristiques :

* surface ;
* nombre de pièces ;
* âge du logement ;
* distance par rapport au centre-ville.

Le projet ne se limite pas à l’entraînement d’un modèle. Il couvre l’ensemble du cycle de vie des données et du modèle : ingestion, stockage, transformation, qualité, orchestration, entraînement, suivi des expériences, registry, serving, tests, conteneurisation, CI/CD et monitoring.

---

## 2. Architecture générale

Le pipeline suit l’architecture suivante :

```text
houses.CSV
    |
    v
dlt
Ingestion automatisée
    |
    v
DuckDB
raw_data.houses
    |
    v
dbt
staging.stg_houses
    |
    v
analytics.ml_houses
    |
    +--> Tests de qualité
    +--> Data Contract
    +--> Freshness
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
MLflow Tracking
Experiments / Runs / Metrics / Artifacts
    |
    v
MLflow Model Registry
HousePriceModel@champion
    |
    v
FastAPI
/health
/predict
/metrics
/ml-metrics
/drift
    |
    v
Docker
    |
    v
GitHub Actions
Tests + Vérification + Build Docker
    |
    v
Monitoring & Observabilité
```

---

## 3. Technologies utilisées

| Domaine          | Technologie                | Rôle                               |
| ---------------- | -------------------------- | ---------------------------------- |
| Versionnement    | Git / GitHub               | Gestion du code et historique      |
| Ingestion        | dlt                        | Ingestion automatisée              |
| Stockage         | DuckDB                     | Base analytique locale             |
| Transformation   | dbt                        | Transformation et modélisation     |
| Qualité          | dbt tests / Data Contract  | Contrôle de qualité                |
| Orchestration    | Dagster                    | Orchestration du pipeline          |
| Machine Learning | Scikit-learn               | Entraînement des modèles           |
| Tracking         | MLflow                     | Suivi des expériences              |
| Registry         | MLflow Model Registry      | Versionnement des modèles          |
| Serving          | FastAPI / Uvicorn          | API de prédiction                  |
| Tests            | Pytest                     | Tests automatisés                  |
| Conteneurisation | Docker                     | Portabilité du service             |
| CI/CD            | GitHub Actions             | Automatisation des tests et builds |
| Monitoring       | FastAPI + métriques custom | Observabilité API et ML            |

---

## 4. Structure du projet

```text
mini-house-mlops/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── api/
│   ├── main.py
│   └── reference_stats.json
│
├── data/
│   └── houses.CSV
│
├── dbt_project/
│
├── ingestion/
│
├── ml/
│   ├── train.py
│   ├── register_best_model.py
│   ├── predict_from_registry.py
│   └── create_reference_stats.py
│
├── orchestration/
│
├── src/
│
├── tests/
│   └── test_api.py
│
├── warehouse/
│   └── house_prices.duckdb
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements-api.txt
├── requirements.txt
└── README.md
```

Certains répertoires générés localement, tels que `.venv`, `mlartifacts`, caches Python, logs et bases locales MLflow, ne sont pas destinés à être intégrés à l’image Docker.

---

## 5. Pipeline DataOps

### 5.1 Source de données

Le projet utilise le fichier :

```text
data/houses.CSV
```

Les données représentent des logements avec notamment :

```text
surface
rooms
age
distance_city
price
```

### 5.2 Ingestion avec dlt

`dlt` automatise l’ingestion des données vers DuckDB.

Les données brutes sont stockées dans une couche de type :

```text
raw_data.houses
```

### 5.3 Stockage DuckDB

La base principale est :

```text
warehouse/house_prices.duckdb
```

DuckDB permet de disposer d’un stockage analytique local, léger et adapté au projet.

### 5.4 Transformation avec dbt

dbt permet de transformer les données brutes en données propres et exploitables.

Le pipeline construit notamment :

```text
raw_data.houses
        ↓
staging.stg_houses
        ↓
analytics.ml_houses
```

La table utilisée par le Machine Learning est :

```text
analytics.ml_houses
```

---

## 6. Qualité des données

La qualité est contrôlée avant l’utilisation des données par le modèle.

Le projet couvre notamment :

* valeurs nulles ;
* unicité des identifiants ;
* validité des valeurs ;
* freshness des sources ;
* Data Contract ;
* documentation des modèles dbt.

Un problème de qualité rencontré pendant le développement concernait notamment une valeur invalide `-55`, ce qui a permis de vérifier le fonctionnement réel des tests de validité.

---

## 7. Orchestration avec Dagster

Dagster permet d’automatiser et de superviser les différentes étapes DataOps.

Le pipeline orchestre notamment :

```text
Ingestion
   ↓
Freshness
   ↓
dbt run
   ↓
dbt test
```

Dagster fournit également les logs, la visibilité sur les exécutions, la gestion des dépendances entre étapes et la possibilité de mettre en place des retries ou des schedules.

---

## 8. Machine Learning

Le problème traité est une **régression**.

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

Deux modèles ont été entraînés :

```text
LinearRegression
RandomForestRegressor
```

Le dataset préparé contient seulement 20 observations. Les résultats ont donc une vocation principalement pédagogique et ne doivent pas être interprétés comme les performances d’un modèle immobilier de production à grande échelle.

### Résultats obtenus

#### Linear Regression — Train

```text
MAE  : 10 093.76
RMSE : 13 267.19
R²   : 0.99897
```

#### Linear Regression — Test

```text
MAE  : 47 891.96
RMSE : 58 847.74
R²   : 0.98933
```

#### Random Forest — Train

```text
MAE  : 31 343.75
RMSE : 47 900.88
R²   : 0.98660
```

#### Random Forest — Test

```text
MAE  : 134 975.00
RMSE : 138 081.60
R²   : 0.94127
```

La baseline obtenue avait une MAE de :

```text
562 500
```

La régression linéaire a obtenu la meilleure `test_mae` et a donc été retenue comme meilleur modèle dans les expériences réalisées.

---

## 9. MLflow Tracking

MLflow est utilisé pour conserver les expériences de Machine Learning.

L’expérience principale est :

```text
house_price_prediction
```

Les métriques enregistrées comprennent :

```text
train_mae
train_rmse
train_r2

test_mae
test_rmse
test_r2

baseline_mae
```

Les paramètres des modèles ainsi que les artefacts sont également enregistrés.

---

## 10. Model Registry

Le meilleur modèle est sélectionné automatiquement selon :

```text
metrics.test_mae ASC
```

Il est ensuite enregistré dans MLflow Model Registry sous le nom :

```text
HousePriceModel
```

L’alias utilisé pour identifier le modèle actuellement déployé est :

```text
champion
```

Le modèle consommé par l’API correspond donc à :

```text
models:/HousePriceModel@champion
```

Cette approche permet de changer le modèle déployé sans modifier le code de l’API.

---

## 11. API FastAPI

L’API charge automatiquement le modèle `champion` depuis MLflow lors de son démarrage.

### Documentation Swagger

```text
http://localhost:8000/docs
```

### Health check

```http
GET /health
```

Permet de vérifier la disponibilité de l’API.

### Prédiction

```http
POST /predict
```

Exemple :

```json
{
  "surface": 120,
  "rooms": 4,
  "age": 10,
  "distance_city": 5
}
```

Exemple de réponse :

```json
{
  "predicted_price": 1234567.89,
  "model": "HousePriceModel@champion"
}
```

Les entrées sont validées avec Pydantic.

Par exemple :

```json
{
  "surface": -20,
  "rooms": 4,
  "age": 10,
  "distance_city": 5
}
```

produit une réponse HTTP :

```text
422 Unprocessable Entity
```

---

## 12. Tests automatisés

Les tests sont réalisés avec Pytest et FastAPI TestClient.

Ils utilisent notamment un `FakeModel` afin de tester l’API sans dépendre du serveur MLflow réel.

La commande utilisée est :

```bash
python -m pytest -v
```

La suite actuelle contient :

```text
9 tests
9 passed
```

Elle vérifie notamment :

* `/health` ;
* prédiction valide ;
* surface négative ;
* nombre de pièces nul ;
* âge négatif ;
* champ manquant ;
* `/metrics` ;
* `/ml-metrics` ;
* détection de dérive.

---

## 13. Docker

L’API est conteneurisée avec Docker.

### Construire l’image

```bash
docker build -t mini-house-api:1.0 .
```

### Lancer le conteneur

MLflow étant exécuté sur la machine hôte, Docker Desktop utilise :

```text
host.docker.internal
```

La commande utilisée est :

```bash
docker run -d --name mini-house-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 mini-house-api:1.0
```

### Vérification

```bash
docker ps
```

Le conteneur doit atteindre l’état :

```text
healthy
```

Le Dockerfile inclut en effet un `HEALTHCHECK` qui interroge régulièrement :

```text
http://localhost:8000/health
```

---

## 14. CI/CD avec GitHub Actions

Le workflow est défini dans :

```text
.github/workflows/ci.yml
```

Il est automatiquement déclenché lors d’un :

```text
push
```

ou d’une :

```text
pull request
```

Le pipeline réalise :

```text
Checkout du dépôt
        ↓
Installation Python 3.10
        ↓
Installation des dépendances
        ↓
Vérification syntaxique Python
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

Le build Docker de CI utilise :

```bash
docker build -t mini-house-api:ci .
```

Le workflow GitHub Actions a été exécuté avec succès.

---

## 15. Monitoring et observabilité

Le projet couvre plusieurs niveaux de monitoring.

### Disponibilité

```http
GET /health
```

complété par le `HEALTHCHECK` Docker.

### Monitoring API

```http
GET /metrics
```

Expose notamment :

```text
total_requests
successful_requests
client_errors
server_errors
last_response_time_ms
average_response_time_ms
```

### Monitoring ML

```http
GET /ml-metrics
```

Récupère depuis MLflow les métriques du modèle actuellement associé à l’alias `champion`.

Les valeurs ne sont pas codées en dur dans FastAPI : elles sont récupérées depuis la run MLflow associée au modèle enregistré.

### Data Drift

```http
GET /drift
```

La dérive simple compare les moyennes des données reçues en production avec les statistiques des données utilisées pour l’entraînement.

Les statistiques de référence sont générées depuis :

```text
analytics.ml_houses
```

et enregistrées dans :

```text
api/reference_stats.json
```

Le dataset de référence contient :

```text
20 observations
```

Les moyennes de référence sont :

```text
surface       : 105.50
rooms         : 3.40
age           : 5.95
distance_city : 4.86
```

Le mécanisme utilise actuellement un seuil heuristique de :

```text
20 %
```

Si l’écart relatif entre une moyenne de production et la moyenne de référence dépasse ce seuil, une dérive est signalée.

Cette méthode est volontairement simple et pédagogique. Une solution industrielle pourrait utiliser des méthodes statistiques plus avancées.

---

## 16. Installation

### Prérequis

Le projet a été développé avec :

```text
Python 3.10
Git
Docker Desktop
WSL2 sous Windows
```

Créer l’environnement virtuel :

```bash
python -m venv .venv
```

Sous Windows :

```bash
.venv\Scripts\activate
```

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

---

## 17. Lancer MLflow

Depuis la racine du projet :

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000
```

Interface MLflow :

```text
http://localhost:5000
```

---

## 18. Lancer l’API sans Docker

Avec MLflow déjà actif :

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Puis ouvrir :

```text
http://localhost:8000/docs
```

---

## 19. Lancer l’API avec Docker

Construire :

```bash
docker build -t mini-house-api:1.0 .
```

Puis lancer :

```bash
docker run -d --name mini-house-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 mini-house-api:1.0
```

Vérifier :

```bash
docker ps
```

---

## 20. Statistiques de référence pour le drift

Pour régénérer les statistiques de référence :

```bash
python ml/create_reference_stats.py
```

Le script lit :

```text
analytics.ml_houses
```

dans DuckDB et génère :

```text
api/reference_stats.json
```

---

## 21. Points d’accès principaux

| Endpoint      | Fonction                   |
| ------------- | -------------------------- |
| `/docs`       | Documentation Swagger      |
| `/health`     | Disponibilité du service   |
| `/predict`    | Prédiction du prix         |
| `/metrics`    | Monitoring de l’API        |
| `/ml-metrics` | Métriques ML du champion   |
| `/drift`      | Détection simple de dérive |

---

## 22. Points pédagogiques importants

Ce projet permet d’illustrer plusieurs principes fondamentaux de DataOps et MLOps :

```text
Automatiser plutôt qu'exécuter manuellement
Tester les données avant de les utiliser
Séparer ingestion, transformation et ML
Rendre les expériences reproductibles
Tracer les métriques et les paramètres
Versionner les modèles
Découpler le modèle de l'API
Tester le serving automatiquement
Conteneuriser le service
Automatiser les contrôles avec CI/CD
Monitorer le service et les données
```

---

## 23. Limites

Le projet est volontairement pédagogique.

La principale limite concerne la taille du dataset :

```text
20 observations
```

Les très bonnes performances obtenues par certains modèles ne doivent donc pas être interprétées comme une preuve de généralisation sur un véritable marché immobilier.

La dérive est également détectée avec une approche simple basée sur l’écart relatif des moyennes.

---

## 24. Évolutions possibles

Des extensions futures pourraient inclure :

* dataset immobilier réel et plus volumineux ;
* déploiement cloud ;
* registry d’images Docker ;
* Continuous Deployment réel ;
* Prometheus et Grafana ;
* monitoring avancé des modèles ;
* Evidently ou solution équivalente pour la dérive ;
* authentification de l’API ;
* base de données de monitoring persistante ;
* alertes automatiques ;
* réentraînement automatique du modèle.

---

## 25. Conclusion

Mini House MLOps met en œuvre une chaîne complète :

```text
Data
→ DataOps
→ Qualité
→ Orchestration
→ Machine Learning
→ Experiment Tracking
→ Model Registry
→ Serving
→ Testing
→ Docker
→ CI/CD
→ Monitoring
```

L’objectif principal est de montrer qu’un projet Machine Learning ne se limite pas à entraîner un modèle : il faut également assurer la qualité des données, la reproductibilité, le versionnement, l’automatisation, le déploiement, les tests et l’observabilité.
