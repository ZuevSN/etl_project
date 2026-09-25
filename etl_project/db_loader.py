# etl_project.db_loader.py

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import etl_project.csv_handler as h
import logging
from etl_project.decorators import isolated_process
import pandas as pd
from etl_project.models import ETLContext
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


@isolated_process("Тест подключения к базе")
def test_connection(ctx: ETLContext) -> None:
    try:
        with ctx.engine.begin() as conn:
            logger.info("Успешное подключение к PostgreSQL!")
            logger.debug("Делаю просто запрос к базе")
            result = conn.execute(text("SELECT version();"))
            logger.info(result.fetchone()[0])
            return True
    except Exception as e:
        logger.error(f"Ошибка подключения к БД. Детали: {e}", exc_info=True)
        raise Exception("Ошибка подключения к БД") from e


@isolated_process("Загрузка сырых данных")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (ConnectionError, OperationalError, OSError, TimeoutError)
    ),
)
def load_raw_data(ctx: ETLContext) -> int:
    logger.debug("Читаю csv в pandas dataframe")
    df = h.read_csv_to_df(ctx.csv_path, ctx.dtype_dict)
    if df.empty:
        raise ValueError("Dataframe is empty")
    logger.debug("Привожу колонки к нормальному виду")
    df = normalize_column(df)
    df.to_sql("raw_data", con=ctx.engine, if_exists="replace", index=False)
    return len(df)


@isolated_process("Создание индекса на Age")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (ConnectionError, OperationalError, OSError, TimeoutError)
    ),
)
def create_index_age(ctx: ETLContext) -> None:
    query = """
        EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
        SELECT * FROM raw_data WHERE age = :age
"""
    with ctx.engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_age ON raw_data (Age)"))
        result = conn.execute(text(query), {"age": 76})
        explain_output = result.fetchall()
        for row in explain_output:
            logger.info(row[0])


@isolated_process("Загрузка преобразованных даных")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (ConnectionError, OperationalError, OSError, TimeoutError)
    ),
)
def transform_data(ctx: ETLContext) -> None:
    with ctx.engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS processed_data"))
        query = """
            CREATE TABLE processed_data AS
            WITH RANKED_DATA AS (
            SELECT *, RANK()  OVER (PARTITION BY pclass
            ORDER BY fare DESC) as fare_rank_in_class
            FROM raw_data
            WHERE age = :age
            )
            SELECT *, fare * :multiplier as tax
            from RANKED_DATA
            where fare_rank_in_class <= 3
"""
        conn.execute(text(query), {"multiplier": ctx.multiplier, "age": ctx.age})


# приводим имена к колонок стандартному виду
# убираем прбелы по краям
# переводим в нижний регистр
# заменяем пробелы внутри на подчеркивание
def normalize_column(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    return df


@isolated_process("Загрузчик")
def loader(ctx):
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
