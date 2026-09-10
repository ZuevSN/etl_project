# etl_project.db_loader.py

from sqlalchemy import create_engine, text
import etl_project.csv_handler as h
from etl_project import filter_func as f
import logging
from etl_project.decorators import isolated_process
from etl_project.models import ETLContext

logger = logging.getLogger(__name__)

# Строка подключения: dialect+driver://username:password@host:port/database


@isolated_process("Тест подключения к базе")
def test_connection(engine):
    try:
        with engine.connect() as connection:
            logger.info("Успешное подключение к PostgreSQL!")
            # Простой тестовый запрос
            result = connection.execute(text("SELECT version();"))
            logger.info(result.fetchone()[0])
            return True
    except Exception as e:
        raise Exception("Ошибка подключения к БД") from e


@isolated_process("Обработка и загрузка файла в базу")
def process_df(ctx):
    df = h.read_csv_to_df(ctx.csv_path)
    df = f.dfEqValue(df, "Age", 30)
    df["Tax"] = df["Fare"].astype(float) * 0.2
    logger.info("Данные подготовлены для загрузки")
    df.to_sql(name="processed_data", con=ctx.engine, if_exists="replace", index=False)
    logger.info("данные загружены")
    return df


@isolated_process("Загрузчик")
def loader(ctx):
    if test_connection(ctx.engine):
        process_df(ctx)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loader()
