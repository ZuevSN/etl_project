from sqlalchemy import create_engine, text

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

if __name__ == "__main__":
    test_connection()