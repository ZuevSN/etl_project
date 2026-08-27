#etl_project.db_loader.py

from sqlalchemy import create_engine, text
import etl_project.csv_handler as h
from etl_project import filter_func as f
import logging
from etl_project.decorators import isolated_process

logger = logging.getLogger(__name__)

# Строка подключения: dialect+driver://username:password@host:port/database
DATABASE_URL = "postgresql+psycopg2://dev:devpassword@localhost:5432/etl_db"
engine = create_engine(DATABASE_URL)

@isolated_process("Тест подключения к базе")
def test_connection():
    try:
        with engine.connect() as connection:
            logger.info("Успешное подключение к PostgreSQL!")
            # Простой тестовый запрос
            result = connection.execute(text("SELECT version();"))
            logger.info(result.fetchone()[0])
    except Exception as e:
        raise Exception(f"Ошибка подключения к БД") from e

@isolated_process("Обработка и загрузка файла в базу")
def process_df():
    df = h.read_csv_to_df('tested.csv')
    df = f.dfEqValue(df,'Age',30)
    df['Tax'] = df['Fare'].astype(float) * 0.2
    print(df)
    df.to_sql(name='processed_data', con=engine,
              if_exists='replace',index=False)
    return df


def loader():
    test_connection()
    process_df()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    loader()