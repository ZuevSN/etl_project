#etl_project.db_loader.py

from sqlalchemy import create_engine, text
import etl_project.csv_handler as h
from etl_project import filter_func as f
import logging
from etl_project.decorators import isolated_process

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
    except Exception as e:
        raise Exception(f"Ошибка подключения к БД") from e

@isolated_process("Обработка и загрузка файла в базу")
def process_df(engine):
    df = h.read_csv_to_df('tested.csv')
    df = f.dfEqValue(df,'Age',30)
    df['Tax'] = df['Fare'].astype(float) * 0.2
    df.to_sql(name='processed_data', con=engine,
            if_exists='replace',index=False)
    return df

@isolated_process("Загрузчик")
def loader(DATABASE_URL):
    if not DATABASE_URL:
        raise ValueError("Отсутствует переменная окружения DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    if test_connection(engine):
        process_df(engine)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    loader()