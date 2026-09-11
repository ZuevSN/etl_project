# airflow.dags.etl_dag.py
from datetime import datetime
import sys

sys.path.insert(0,'/opt/airflow')

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
import etl_project.models as m


import etl_project.db_loader as loader

def _get_etl_context():
    csv_path = Variable.get('etl_csv_path')
    dtype_dict = Variable.get('csv_dtype_map', deserialize_json=True)
    hook = PostgresHook(postgres_conn_id='etl_postgres')
    engine = hook.get_sqlalchemy_engine()
    ctx = m.ETLContext(
         engine=engine,
        csv_path=csv_path,
        dtype_dict=dtype_dict
    )
    return ctx
"""
def run_loader():
    import os
    from pathlib import Path

    # указываем путь до файла
    #project_dir = Path('/opt/airflow/etl_project')
    #csv_path = project_dir.parent  / 'tested.csv'
    csv_path = Variable.get('etl_csv_path')
    dtype_dict = Variable.get('csv_dtype_map', deserialize_json=True)
    hook = PostgresHook(postgres_conn_id='etl_postgres')
    engine = hook.get_sqlalchemy_engine()
    try:
    #db_url = f'postgresql+psycopg2://{conn.login}:{conn.password}:@{conn.host}:{conn.port}/{conn.schema}'
        ctx = m.ETLContext(
            engine=engine,
            csv_path=csv_path,
            dtype_dict=dtype_dict
        )


    # if not csv_path.exists():
    #    raise FileNotFoundError(f"CSV файл не найден: {csv_path}")

    # ВАЖНО: используем имя контейнера PostgreSQL, а не localhost!
    # db_url = "postgresql+psycopg2://dev:devpassword@etl_postgres:5432/etl_db"
    ##loader(db_url, csv_path = str(csv_path))
        loader(ctx)
    finally:
        engine.dispose()
"""
with DAG(
    dag_id='etl_pipeline',
    start_date=datetime(2026, 1, 1),
    #schedule=None,  # запуск вручную
    #schedule='@daily', ежедневно
    schedule='0 2 * * *',  # Стало (каждый день в 02:00 по времени сервера)
    catchup=False,  # Не запускать пропущенные дни
    tags=['etl', 'learning'],
) as dag:
    
    # "классический" способ объявления задачи в Airflow
    #task_load = PythonOperator(
    #    task_id='load_to_postgres',
    #    python_callable=run_loader,
    #)
    
    @task
    def load_raw_data():
        ctx = _get_etl_context()
        try:
            loader.load_raw_data(ctx)
            loader.create_index_age(ctx)
        finally:
            ctx.engine.dispose()

    @task
    def transform_data():
        ctx = _get_etl_context()
        try:
            loader.transform_data(ctx)
        finally:
            ctx.engine.dispose()
    
    load_raw_data() >> transform_data()