from datetime import datetime
import sys

# Добавляем путь к твоему проекту
sys.path.insert(0,'/opt/airflow')

from airflow import DAG
from airflow.models import Variable, Connection
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook

from etl_project.db_loader import loader

def run_loader():
    import os
    from pathlib import Path

    # указываем путь до файла
    #project_dir = Path('/opt/airflow/etl_project')
    #csv_path = project_dir.parent  / 'tested.csv'
    csv_path = Variable.get('etl_csv_path')
    conn = BaseHook.get_connection('postgres_etl')
    db_url = f'postgresql+psycopg2://{conn.login}:{conn.password}:@{conn.host}:{conn.port}/{conn.schema}'
    # if not csv_path.exists():
    #    raise FileNotFoundError(f"CSV файл не найден: {csv_path}")

    # ВАЖНО: используем имя контейнера PostgreSQL, а не localhost!
    # db_url = "postgresql+psycopg2://dev:devpassword@etl_postgres:5432/etl_db"
    loader(db_url, csv_path = str(csv_path))

with DAG(
    dag_id='etl_pipeline',
    start_date=datetime(2026, 1, 1),
    #schedule=None,  # запуск вручную
    #schedule='@daily', ежедневно
    schedule='0 2 * * *',  # Стало (каждый день в 02:00 по времени сервера)
    catchup=False,  # Не запускать пропущенные дни
    tags=['etl', 'learning'],
) as dag:
    
    task_load = PythonOperator(
        task_id='load_to_postgres',
        python_callable=run_loader,
    )