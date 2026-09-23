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

logger = logging.getLogger(__name__)


def alert_on_failure(context):
    task_id = context["task_instance"].task_id
    dag_id = context["dag"].dag_id
    exception = context["exception"]

    logging.error(f"ALERT: {dag_id}.{task_id} failed with {exception}")


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
        raise ConnectionError(f"Не удалось подключиться к БД {e}") from e


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


with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",  # Стало (каждый день в 02:00 по времени сервера)
    catchup=False,  # Не запускать пропущенные дни
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": alert_on_failure,
    },
    tags=["etl", "learning"],
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
            DFLength = loader.load_raw_data(ctx)
            loader.create_index_age(ctx)
            return {"row_count": DFLength}
        finally:
            ctx.engine.dispose()

    @task
    def transform_data(metadata: dict):
        ctx = _get_etl_context()
        try:
            logging.info(f"Transforming {metadata['row_count']} rows")
            if metadata["row_count"] == 0:
                raise ValueError("No data for transform")
            loader.transform_data(ctx)
        finally:
            ctx.engine.dispose()

    transform_data(load_raw_data())
