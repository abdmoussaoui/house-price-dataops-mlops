from pathlib import Path
import shutil
import subprocess
import sys

import dagster as dg


ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT = ROOT / "dbt_project"


def run_command(context, command):
    command = [str(item) for item in command]

    context.log.info(
        "Commande exécutée : " + " ".join(command)
    )

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        context.log.info(result.stdout)

    if result.returncode != 0:

        if result.stderr:
            context.log.error(result.stderr)

        raise dg.Failure(
            description=(
                "La commande a échoué : "
                + " ".join(command)
            )
        )


def get_dbt_executable():

    dbt_executable = shutil.which("dbt")

    if dbt_executable is None:
        raise RuntimeError(
            "dbt est introuvable. "
            "Vérifie que ton environnement .venv est actif."
        )

    return dbt_executable


@dg.op(
    retry_policy=dg.RetryPolicy(
        max_retries=1,
        delay=2,
    )
)
def ingest_houses(context) -> str:

    context.log.info(
        "Début de l'ingestion avec dlt."
    )

    run_command(
        context,
        [
            sys.executable,
            ROOT / "ingestion" / "load_houses.py",
        ],
    )

    context.log.info(
        "Ingestion terminée."
    )

    return "ingestion_ok"


@dg.op
def check_source_freshness(
    context,
    ingestion_status: str,
) -> str:

    context.log.info(
        "Vérification de la fraîcheur des données."
    )

    run_command(
        context,
        [
            get_dbt_executable(),
            "source",
            "freshness",
            "--project-dir",
            DBT_PROJECT,
            "--profiles-dir",
            DBT_PROJECT,
        ],
    )

    return "freshness_ok"


@dg.op
def build_dbt_models(
    context,
    freshness_status: str,
) -> str:

    context.log.info(
        "Construction des modèles dbt."
    )

    run_command(
        context,
        [
            get_dbt_executable(),
            "run",
            "--project-dir",
            DBT_PROJECT,
            "--profiles-dir",
            DBT_PROJECT,
        ],
    )

    return "dbt_models_ok"


@dg.op
def test_dbt_models(
    context,
    dbt_status: str,
):

    context.log.info(
        "Exécution des tests de qualité dbt."
    )

    run_command(
        context,
        [
            get_dbt_executable(),
            "test",
            "--project-dir",
            DBT_PROJECT,
            "--profiles-dir",
            DBT_PROJECT,
        ],
    )

    context.log.info(
        "Tous les tests sont terminés."
    )


@dg.job
def house_data_pipeline():

    ingestion = ingest_houses()

    freshness = check_source_freshness(
        ingestion
    )

    dbt_models = build_dbt_models(
        freshness
    )

    test_dbt_models(
        dbt_models
    )


defs = dg.Definitions(
    jobs=[
        house_data_pipeline,
    ]
)