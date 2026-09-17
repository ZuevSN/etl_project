# etl_project.db_loader.py

from sqlalchemy import text
import etl_project.csv_handler as h
import logging
from etl_project.decorators import isolated_process
from pandas import DataFrame
from etl_project.models import ETLContext

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
def load_raw_data(ctx: ETLContext) -> None:
    logger.debug("Читаю csv в pandas dataframe")
    df = h.read_csv_to_df(ctx.csv_path, ctx.dtype_dict)
    if df.empty:
        raise ValueError("Dataframe is empty")
    logger.debug("Привожу колонки к нормальному виду")
    df = normalize_column(df)
    df.to_sql("raw_data", con=ctx.engine, if_exists="replace", index=False)


@isolated_process("Создание индекса на Age")
def create_index_age(ctx: ETLContext) -> None:
    with ctx.engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_age ON raw_data (Age)"))


@isolated_process("Загрузка преобразованных даных")
def transform_data(ctx: ETLContext) -> None:
    with ctx.engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS processed_data"))
        query = """
            CREATE TABLE processed_data AS
            SELECT *, Fare * :multiplier as Tax
            FROM raw_data
            WHERE Age = :age
"""
        conn.execute(text(query), {"multiplier": ctx.multiplier, "age": ctx.age})


# приводим имена к колонок стандартному виду
# убираем прбелы по краям
# переводим в нижний регистр
# заменяем пробелы внутри на подчеркивание
def normalize_column(df: DataFrame) -> DataFrame:
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
