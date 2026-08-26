#etl_project.db_loader.py

from sqlalchemy import create_engine, text
import etl_project.csv_handler as h
from etl_project import filter_func as f

# Строка подключения: dialect+driver://username:password@host:port/database
DATABASE_URL = "postgresql+psycopg2://dev:devpassword@localhost:5432/etl_db"
engine = create_engine(DATABASE_URL)

def test_connection():
    try:
        with engine.connect() as connection:
            print("Успешное подключение к PostgreSQL!")
            # Простой тестовый запрос
            result = connection.execute(text("SELECT version();"))
            print(result.fetchone()[0])
    except Exception as e:
        print(f"Ошибка подключения: {e}")

def process_df():
    try:
        df = h.read_csv_to_df('tested.csv')
        df = f.dfEqValue(df,'Age',30)
        print(df)
        return df
    except Exception as e:
        print(f'{type(e).__name__}: {e}')

def main():
    test_connection()
    process_df()


if __name__ == "__main__":
    main()