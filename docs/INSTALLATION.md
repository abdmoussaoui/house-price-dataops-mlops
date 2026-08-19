# Guide d'installation — Mini House MLOps

## 1. Objectif

Ce document décrit les étapes nécessaires pour installer et préparer l’environnement du projet **Mini House MLOps — Observatoire intelligent des prix immobiliers**.

L’objectif est de permettre à un nouvel utilisateur ou membre de l’équipe de reconstruire l’environnement du projet et d’utiliser les différents composants :

* Python ;
* dlt ;
* DuckDB ;
* dbt ;
* Dagster ;
* Scikit-learn ;
* MLflow ;
* FastAPI ;
* Pytest ;
* Docker ;
* Git ;
* GitHub Actions.

Le projet a principalement été développé et testé sous **Windows avec Python 3.10, WSL2 et Docker Desktop**.

---

# 2. Prérequis

Avant d’installer le projet, vérifier que les outils suivants sont disponibles.

## 2.1 Git

Git est utilisé pour récupérer le dépôt et gérer le versionnement.

Vérification :

```bash
git --version
```

Une version de Git doit être affichée.

---

## 2.2 Python

Le projet utilise :

```text
Python 3.10
```

Vérification :

```bash
python --version
```

Résultat attendu :

```text
Python 3.10.x
```

Il est recommandé de conserver Python 3.10 afin de rester cohérent avec l’environnement utilisé pendant le développement du projet.

---

## 2.3 pip

Vérifier que `pip` est disponible :

```bash
python -m pip --version
```

---

## 2.4 Docker Desktop

Docker est nécessaire pour la conteneurisation de l’API FastAPI.

Vérification :

```bash
docker --version
```

Puis :

```bash
docker info
```

Le premier test Docker peut être réalisé avec :

```bash
docker run hello-world
```

Une installation fonctionnelle doit afficher notamment :

```text
Hello from Docker!
```

---

# 3. WSL2 sous Windows

Pour Docker Desktop sous Windows, le projet a été exécuté avec **WSL2**.

Vérification :

```powershell
wsl --version
```

Puis :

```powershell
wsl --status
```

L’environnement utilisé pendant le projet avait notamment :

```text
Distribution par défaut : Ubuntu
Version par défaut : 2
```

Si WSL n’est pas installé, il peut être installé depuis PowerShell administrateur :

```powershell
wsl --install
```

Un redémarrage de Windows peut être nécessaire.

---

# 4. Récupérer le projet

Cloner le dépôt GitHub :

```bash
git clone <URL_DU_DEPOT_GITHUB>
```

Puis accéder au projet :

```bash
cd mini-house-mlops
```

Sous Windows, le projet utilisé pendant le développement était par exemple situé dans :

```text
D:\cours master\s2\MLops\comprendre projet\mini-house-mlops
```

Ce chemin est uniquement un exemple local et n’est pas obligatoire.

---

# 5. Structure principale

Après récupération du dépôt, l’arborescence principale doit ressembler à :

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
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements-api.txt
├── requirements.txt
└── README.md
```

Certains fichiers ou dossiers sont générés localement et peuvent ne pas être présents immédiatement après le clonage, par exemple :

```text
.venv/
mlflow.db
mlartifacts/
logs/
.pytest_cache/
```

---

# 6. Création de l'environnement virtuel Python

Depuis la racine du projet :

```bash
python -m venv .venv
```

Cela crée un environnement Python isolé dans :

```text
.venv/
```

L’utilisation d’un environnement virtuel permet d’éviter les conflits avec les bibliothèques Python installées globalement sur la machine.

---

# 7. Activation de l'environnement virtuel

## Windows CMD

```cmd
.venv\Scripts\activate
```

## Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Une fois activé, le terminal doit généralement afficher :

```text
(.venv)
```

avant le chemin courant.

Exemple :

```text
(.venv) D:\...\mini-house-mlops>
```

---

# 8. Mise à jour de pip

Après activation de l’environnement :

```bash
python -m pip install --upgrade pip
```

---

# 9. Installation des dépendances principales

Le projet possède un fichier :

```text
requirements.txt
```

contenant les dépendances générales utilisées pendant le développement.

Installation :

```bash
python -m pip install -r requirements.txt
```

Cette installation prépare notamment l’environnement nécessaire aux différentes briques DataOps et MLOps du projet.

---

# 10. Dépendances de l'API

L’API possède également un fichier de dépendances spécifique :

```text
requirements-api.txt
```

Son contenu utilisé dans le projet est :

```text
fastapi==0.141.1
uvicorn==0.52.3
mlflow==3.15.1
pandas==2.3.3
scikit-learn==1.7.2
```

Ces dépendances sont principalement utilisées pour :

| Dépendance   | Utilisation                           |
| ------------ | ------------------------------------- |
| FastAPI      | Création de l’API                     |
| Uvicorn      | Serveur ASGI                          |
| MLflow       | Chargement du modèle champion         |
| Pandas       | Préparation des données de prédiction |
| Scikit-learn | Exécution du modèle ML                |

Installation manuelle si nécessaire :

```bash
python -m pip install -r requirements-api.txt
```

---

# 11. Vérification de l'installation Python

Vérifier que les principaux packages sont accessibles :

```bash
python -c "import fastapi; import mlflow; import pandas; import sklearn; print('Installation Python OK')"
```

Résultat attendu :

```text
Installation Python OK
```

---

# 12. Préparation des données

La source utilisée par le projet est :

```text
data/houses.CSV
```

Le fichier doit être présent avant l’exécution du pipeline DataOps.

Les principales colonnes utilisées sont :

```text
surface
rooms
age
distance_city
price
```

---

# 13. Base DuckDB

Le pipeline DataOps génère et utilise une base DuckDB :

```text
warehouse/house_prices.duckdb
```

Cette base contient les différentes couches de données utilisées par le projet.

Architecture logique :

```text
raw_data
    ↓
staging
    ↓
analytics
```

La table utilisée par le Machine Learning est :

```text
analytics.ml_houses
```

La base DuckDB peut être générée à partir du pipeline d’ingestion et de transformation du projet.

---

# 14. Configuration dbt

Le projet dbt se trouve dans :

```text
dbt_project/
```

Avant utilisation, vérifier que dbt est installé :

```bash
dbt --version
```

La configuration exacte utilisée par le projet doit correspondre à la base DuckDB locale.

Les transformations dbt permettent notamment de produire :

```text
raw_data.houses
        ↓
staging.stg_houses
        ↓
analytics.ml_houses
```

---

# 15. Vérification de Dagster

Dagster est utilisé pour orchestrer le pipeline DataOps.

Vérifier son installation :

```bash
dagster --version
```

Le code d’orchestration du projet est stocké dans :

```text
orchestration/
```

Dagster intervient après la mise en place de l’ingestion, de DuckDB et de dbt.

---

# 16. Installation et préparation de MLflow

MLflow est utilisé pour :

* le tracking des expériences ;
* les paramètres ;
* les métriques ;
* les artefacts ;
* le Model Registry ;
* la gestion du modèle `champion`.

Vérifier son installation :

```bash
mlflow --version
```

---

# 17. Démarrer le serveur MLflow

Depuis la racine du projet et avec l’environnement virtuel activé :

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000
```

Le serveur doit rester actif dans son terminal.

Depuis Windows, ouvrir ensuite :

```text
http://localhost:5000
```

Remarque :

```text
0.0.0.0
```

est une adresse d’écoute du serveur.

Dans le navigateur, utiliser :

```text
localhost:5000
```

et non :

```text
0.0.0.0:5000
```

---

# 18. Model Registry

L’application FastAPI attend un modèle enregistré dans MLflow sous le nom :

```text
HousePriceModel
```

avec l’alias :

```text
champion
```

L’URI utilisée est :

```text
models:/HousePriceModel@champion
```

Le modèle doit donc avoir été entraîné puis enregistré dans MLflow Model Registry avant le démarrage complet de l’API.

Le script concerné est :

```text
ml/register_best_model.py
```

---

# 19. Générer les statistiques de référence

Le monitoring de dérive utilise le fichier :

```text
api/reference_stats.json
```

Il peut être généré depuis les données ML avec :

```bash
python ml/create_reference_stats.py
```

Le script lit :

```text
analytics.ml_houses
```

dans DuckDB et calcule notamment :

```text
mean
std
min
max
```

pour :

```text
surface
rooms
age
distance_city
```

Le fichier obtenu doit se trouver dans :

```text
api/reference_stats.json
```

---

# 20. Vérifier les tests avant le lancement

La commande validée pendant le développement est :

```bash
python -m pytest -v
```

ou en mode compact :

```bash
python -m pytest -q
```

Attention :

Dans l’environnement Windows utilisé pendant le projet, la commande :

```bash
pytest -q
```

a provoqué un problème d’import :

```text
ModuleNotFoundError: No module named 'api'
```

La commande retenue est donc :

```bash
python -m pytest -q
```

La suite actuelle contient :

```text
9 tests
```

Le résultat attendu est :

```text
9 passed
```

---

# 21. Lancer FastAPI sans Docker

MLflow doit être actif avant de démarrer l’API.

Depuis la racine du projet :

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Puis ouvrir :

```text
http://localhost:8000/docs
```

L’API doit notamment exposer :

```text
GET  /health
POST /predict
GET  /metrics
GET  /ml-metrics
GET  /drift
```

---

# 22. Vérifier l'API

Test de disponibilité :

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

Documentation Swagger :

```text
http://localhost:8000/docs
```

---

# 23. Installation Docker

Docker Desktop doit être démarré avant toute commande Docker.

Vérification :

```bash
docker info
```

Puis éventuellement :

```bash
docker run hello-world
```

---

# 24. Construction de l'image Docker

Depuis la racine du projet :

```bash
docker build -t mini-house-api:1.0 .
```

Le Dockerfile utilise comme image de base :

```text
python:3.10-slim
```

L’image produite est :

```text
mini-house-api:1.0
```

Vérification :

```bash
docker images mini-house-api
```

---

# 25. Connexion Docker vers MLflow

Lorsque MLflow s’exécute directement sur Windows et FastAPI dans Docker, le conteneur ne doit pas utiliser :

```text
127.0.0.1:5000
```

car cette adresse représenterait le conteneur lui-même.

Le projet utilise donc :

```text
host.docker.internal
```

L’URI MLflow du conteneur est :

```text
http://host.docker.internal:5000
```

---

# 26. Lancer le conteneur

Avec MLflow actif :

```bash
docker run -d --name mini-house-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 mini-house-api:1.0
```

Cette commande configure :

```text
Nom du conteneur :
mini-house-api

Port hôte :
8000

Port conteneur :
8000

MLflow :
host.docker.internal:5000
```

---

# 27. Vérifier le conteneur

Exécuter :

```bash
docker ps
```

Après le démarrage, le conteneur doit atteindre l’état :

```text
healthy
```

Le projet utilise un Docker `HEALTHCHECK` basé sur :

```text
http://localhost:8000/health
```

---

# 28. Consulter les logs Docker

Pour afficher les logs :

```bash
docker logs mini-house-api
```

Les logs doivent notamment montrer le chargement du modèle :

```text
models:/HousePriceModel@champion
```

puis le démarrage de FastAPI/Uvicorn.

---

# 29. Arrêter le conteneur

```bash
docker stop mini-house-api
```

---

# 30. Redémarrer le conteneur

```bash
docker start mini-house-api
```

---

# 31. Supprimer le conteneur

Le conteneur doit être arrêté avant sa suppression :

```bash
docker stop mini-house-api
```

Puis :

```bash
docker rm mini-house-api
```

Cette opération ne supprime pas l’image Docker.

---

# 32. Reconstruire l'image après modification

Après modification de :

```text
api/main.py
```

ou d’un autre fichier copié dans l’image :

```bash
docker stop mini-house-api
docker rm mini-house-api
docker build -t mini-house-api:1.0 .
```

Puis relancer :

```bash
docker run -d --name mini-house-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 mini-house-api:1.0
```

Docker peut utiliser son cache pour les layers qui n’ont pas changé.

---

# 33. GitHub Actions

La CI est définie dans :

```text
.github/workflows/ci.yml
```

Aucune installation locale supplémentaire n’est nécessaire pour exécuter GitHub Actions.

Le workflow est exécuté sur l’infrastructure GitHub lors d’un :

```text
git push
```

ou d’une Pull Request.

Le pipeline réalise notamment :

```text
Checkout
   ↓
Python 3.10
   ↓
Installation des dépendances
   ↓
Vérification syntaxique
   ↓
Pytest
   ↓
Docker Build
```

---

# 34. Vérifier Git

Depuis la racine du projet :

```bash
git status
```

Pour connaître la branche courante :

```bash
git branch --show-current
```

Pour vérifier le dépôt distant :

```bash
git remote -v
```

---

# 35. Ports utilisés

Le projet utilise principalement :

| Service | Port |
| ------- | ---: |
| MLflow  | 5000 |
| FastAPI | 8000 |

Interface MLflow :

```text
http://localhost:5000
```

Swagger FastAPI :

```text
http://localhost:8000/docs
```

---

# 36. Ordre conseillé de préparation

Pour reconstruire complètement l’environnement, suivre cet ordre :

```text
1. Installer Git
2. Installer Python 3.10
3. Cloner le dépôt
4. Créer .venv
5. Activer .venv
6. Installer requirements.txt
7. Vérifier la source CSV
8. Préparer le pipeline DataOps
9. Générer DuckDB
10. Exécuter les transformations dbt
11. Vérifier les tests qualité
12. Préparer Dagster
13. Entraîner les modèles
14. Démarrer MLflow
15. Enregistrer le meilleur modèle
16. Attribuer l'alias champion
17. Générer reference_stats.json
18. Exécuter Pytest
19. Démarrer FastAPI
20. Installer/démarrer Docker Desktop
21. Construire l'image Docker
22. Lancer le conteneur
23. Vérifier /health
24. Vérifier /predict
25. Vérifier le monitoring
```

---

# 37. Vérification finale de l'installation

L’installation peut être considérée comme opérationnelle lorsque les éléments suivants sont validés :

```text
Python 3.10                     ✅
Environnement virtuel          ✅
Dépendances installées         ✅
Source de données disponible   ✅
DuckDB disponible              ✅
dbt opérationnel               ✅
Dagster opérationnel           ✅
MLflow opérationnel            ✅
Champion enregistré            ✅
9 tests Pytest réussis         ✅
FastAPI opérationnelle         ✅
Docker opérationnel            ✅
Container healthy              ✅
Monitoring accessible          ✅
```

---

# 38. Dépannage rapide

## Erreur : `ModuleNotFoundError: No module named 'api'`

Utiliser :

```bash
python -m pytest -q
```

au lieu de :

```bash
pytest -q
```

---

## MLflow inaccessible dans le navigateur

Ne pas ouvrir :

```text
http://0.0.0.0:5000
```

Utiliser :

```text
http://localhost:5000
```

---

## Docker ne trouve pas MLflow

Dans le conteneur, ne pas utiliser :

```text
http://127.0.0.1:5000
```

Utiliser :

```text
http://host.docker.internal:5000
```

---

## Le conteneur existe déjà

Si Docker affiche un conflit avec :

```text
mini-house-api
```

arrêter puis supprimer l’ancien conteneur :

```bash
docker stop mini-house-api
docker rm mini-house-api
```

Puis relancer la commande `docker run`.

---

## L'API ne démarre pas

Afficher les logs :

```bash
docker logs mini-house-api
```

Vérifier notamment :

* que MLflow est démarré ;
* que le port 5000 est accessible ;
* que `HousePriceModel@champion` existe ;
* que le fichier `reference_stats.json` est présent ;
* que les dépendances sont installées.

---

# 39. Résumé

L’installation complète prépare l’environnement suivant :

```text
Windows
│
├── Python 3.10
│   └── .venv
│
├── DataOps
│   ├── dlt
│   ├── DuckDB
│   ├── dbt
│   └── Dagster
│
├── MLOps
│   ├── Scikit-learn
│   └── MLflow :5000
│
├── Tests
│   └── Pytest
│
└── Docker Desktop
    └── mini-house-api :8000
            │
            └── MLflow via host.docker.internal:5000
```

Une fois cette installation terminée, le projet est prêt pour l’utilisation, l’exécution du pipeline, les prédictions et le monitoring.
