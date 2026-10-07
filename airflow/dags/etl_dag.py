# airflow.dags.etl_dag.py

from datetime import datetime, timedelta
import sys

sys.path.insert(0, "/opt/airflow")
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import etl_project.models as m
import etl_project.db_loader as loader
from pathlib import Path
from sqlalchemy.engine import Engine
from sqlalchemy import text
import logging

import os
from airflow.providers.docker.operators.docker import DockerOperator

logger = logging.getLogger(__name__)

DBT_ENV = {
    "DBT_USER": Variable.get("DBT_USER"),
    "DBT_PASSWORD": Variable.get("DBT_PASSWORD"),
    "DBT_HOST": Variable.get("DBT_HOST"),
    "DBT_PORT": Variable.get("DBT_PORT"),
    "DBT_DBNAME": Variable.get("DBT_DBNAME"),
}

def alert_on_failure(context):
    task_id = context["task_instance"].task_id
    dag_id = context["dag"].dag_id
    exception = context["exception"]

    logger.error(f"ALERT: {dag_id}.{task_id} failed with {exception}")


def validate_values(csv_file: str, age: int) -> None:
    if not csv_file:
        raise ValueError("csv_file is empty or None")
    if age < 0:
        raise ValueError("age should not be negative")


def is_valid_file(path: str | Path) -> Path:
    result_path = Path(path)
    if not result_path.is_file():
        raise FileNotFoundError(f"The file {result_path} does not exist.")
    if result_path.stat().st_size == 0:
        raise ValueError(f"The file {result_path} is empty")
    return result_path


def check_db_connection(engine: Engine) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        raise ConnectionError(f"Не удалось подключиться к БД: {e}") from e


def _get_etl_context():
    csv_path = Variable.get("etl_csv_path")
    dtype_dict = Variable.get("csv_dtype_map", default_var="{}", deserialize_json=True)
    hook = PostgresHook(postgres_conn_id="etl_postgres")
    age = 30
    validate_values(csv_path, age)
    csv_path = is_valid_file(csv_path)
    engine = hook.get_sqlalchemy_engine()
    check_db_connection(engine)
    ctx = m.ETLContext(engine=engine, csv_path=csv_path, dtype_dict=dtype_dict, age=age)
    return ctx

import os

# Читаем путь хоста из .env. Если переменной нет, фоллбэк на путь внутри контейнера (для безопасности)
DBT_PROJECT_HOST_PATH = os.environ.get("DBT_PROJECT_HOST_PATH", "/opt/airflow/dbt_project")
logger.info(f"DEBUG: DBT_PROJECT_HOST_PATH is set to: {DBT_PROJECT_HOST_PATH}")

with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",  # Стало (каждый день в 02:00 по времени сервера)
    catchup=False,  # Не запускать пропущенные дни
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        #"on_failure_callback": alert_on_failure,
    },
    tags=["etl", "learning","dbt"],
) as dag:

    # "классический" способ объявления задачи в Airflow
    """
        task_load = PythonOperator(
        task_id='load_to_postgres',
        python_callable=run_loader,
    )
    """

    # переопределяем параметры DAG при сбоях, на новые
    @task(retries=3, retry_delay=timedelta(minutes=10))
    def load_raw_data():
        ctx = _get_etl_context()
        try:
            row_count = loader.load_raw_data(ctx)
            loader.create_index_age(ctx)
            return {"row_count": row_count}
        finally:
            ctx.engine.dispose()

    dbt_run_task = DockerOperator(
        task_id = 'dbt_run',
        image='ghcr.io/dbt-labs/dbt-postgres:1.8.latest',
        command=['run'],

        #пробрасываем локальную папку с проектом внутрь контейнера dbt
        #volumes=[f"{DBT_PROJECT_PATH}:/usr/app"],
        mounts=[
            {
                "type": "bind",
                "source": DBT_PROJECT_HOST_PATH,
                "target": "/usr/app"
            }
        ],
        working_dir='/usr/app',
        environment=DBT_ENV,
        network_mode='etl_network',
        auto_remove='success',
        mount_tmp_dir=False,
    )

    dbt_test_task = DockerOperator(
        task_id = 'dbt_test',
        image='ghcr.io/dbt-labs/dbt-postgres:1.8.latest',
        command=['test'],
        #volumes=[f"{DBT_PROJECT_PATH}:/usr/app"],
        mounts=[
            {
                "type": "bind",
                "source": DBT_PROJECT_HOST_PATH,
                "target": "/usr/app"
            }
        ],
        working_dir='/usr/app',
        environment=DBT_ENV,
        network_mode='etl_network',
        auto_remove='success',
        mount_tmp_dir=False,
    )


    load_raw_data() >> dbt_run_task >> dbt_test_task
    #transform_data(load_raw_data())
