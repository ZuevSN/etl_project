# etl_project.db_loader.py

from sqlalchemy import create_engine, text
import etl_project.csv_handler as h
from etl_project import filter_func as f
import logging
from etl_project.decorators import isolated_process
from etl_project.models import ETLContext
import pandas as pd

logger = logging.getLogger(__name__)

# Строка подключения: dialect+driver://username:password@host:port/database


@isolated_process("Тест подключения к базе")
def test_connection(ctx):
    try:
        with ctx.engine.begin() as conn:
            logger.info("Успешное подключение к PostgreSQL!")
            # Простой тестовый запрос
            result = conn.execute(text("SELECT version();"))
            logger.info(result.fetchone()[0])
            return True
    except Exception as e:
        logger.error(f"Ошибка подключения к БД. Детали: {e}", exc_info=True)
        raise Exception("Ошибка подключения к БД") from e


@isolated_process("Загрузка сырых данных")
def load_raw_data(ctx):
    df = h.read_csv_to_df(ctx.csv_path, ctx.dtype_dict)
    df = normalize_column(df)
    df.to_sql('raw_data',con=ctx.engine, if_exists='replace', index=False)
    logger.info("Сырые данные загружены")

@isolated_process("Создание индекса на Age")
def create_index_age(ctx):
    with ctx.engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_age ON raw_data (Age)"))

@isolated_process("Загрузка преобразованных даных")
def transform_data(ctx):
    with ctx.engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS processed_data"))
        query = """
            CREATE TABLE processed_data AS
            SELECT *, Fare * :multiplier as Tax
            FROM raw_data
            WHERE Age = :age
"""
        conn.execute(text(query), {'multiplier':ctx.multiplier,'age':ctx.age})
        logger.info("Трансформированные данные загружены")
    #df = h.read_csv_to_df(ctx.csv_path, ctx.dtype_dict)
    #df = normalize_column(df)
    #df.to_sql('raw_data',con=ctx.engine, if_exists='replace', index=False)
    #logger.info("Сырые данные загружены")

# приводим имена к колонок стандартному виду 
# убираем прбелы по краям
# переводим в нижний регистр
# заменяем пробелы внутри на подчеркивание
def normalize_column(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', '_', regex=True)
    )
    return df

@isolated_process("Обработка и загрузка файла в базу")
def process_df(ctx):
    #df = h.read_csv_to_df(ctx.csv_path, ctx.dtype_dict)
    #df = f.dfEqValue(df, "Age", 30)
    #df.to_sql('raw_data',con=ctx.engine, if_exists='replace', index=False)
    load_raw_data(ctx)
    # После загрузки raw_data
    create_index_age(ctx)

# Теперь фильтрация WHERE Age = 30 будет в разы быстрее
    age=30
    query = text("""
        SELECT *, Fare * 0.2 as Tax
        FROM raw_data
        WHERE Age = :age
    """)
    #df["Tax"] = df["Fare"].astype(float) * 0.2
    df_filtered = pd.read_sql(
        query,
        con=ctx.engine,
        params={'age':age}
    )
    logger.info("Данные подготовлены для загрузки")
    df_filtered.to_sql(name="processed_data", con=ctx.engine, if_exists="replace", index=False)
    logger.info("данные загружены")


@isolated_process("Загрузчик")
def loader(ctx):
    if test_connection(ctx):
        load_raw_data(ctx)
        create_index_age(ctx)
        transform_data(ctx)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loader()
