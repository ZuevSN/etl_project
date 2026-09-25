# etl_project.main.py

import logging
import random
import etl_project.csv_handler as h
from etl_project import filter_func as f
from etl_project import db_loader
import etl_project.models as m
from etl_project.decorators import isolated_process
from etl_project.config import AppConfig
from etl_project.process_json import get_dict
from sqlalchemy import create_engine, text
import sqlalchemy.engine as sa_engine
from pathlib import Path
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from sqlalchemy.engine.url import URL

DEFAULTS = {}

conf = AppConfig(DEFAULTS)

logger = logging.getLogger(__name__)


def do_random_ten_list(amount: int) -> list:
    ten_list = []
    if amount - 1 > 0:
        for i in range(amount):
            ten_list.append(random.randint(1, 10))
    return ten_list


def is_even(num: float | int | str | None) -> bool:
    if isinstance(num, int) and not isinstance(num, bool):
        return num % 2 == 0
    return False


def do_sqr_list(my_list: list) -> list:
    new_list = []
    for i in my_list:
        new_list.append(i * i)
    return new_list


@isolated_process("Обработка простого списка")
def process_sample_data() -> None:
    my_list = do_random_ten_list(10)
    my_even_list = list(filter(is_even, my_list))
    my_sqr_list = do_sqr_list(my_even_list)
    logger.info(my_list)
    logger.info(my_even_list)
    logger.info(my_sqr_list)


@isolated_process("Загрузка, обработка, выгрузка csv")
def process_csv_data(path: Path, minAge: int = 30, maxFare: float = 7) -> None:
    logger.info(h.get_len(path))
    filters = [(f.minValue, "Age", minAge), (f.maxValue, "Fare", maxFare)]
    filtered_passenger_data = h.get_rows(path, filters=filters)
    h.write_file("filtered_tested.csv", filtered_passenger_data)
    fixed_passenger_data = h.get_rows(path)
    for row in fixed_passenger_data:
        fare = get_float_or_default(row["Fare"])
        row["Tax"] = fare * 0.2
    h.write_file("tested111.csv", fixed_passenger_data)


def get_float_or_default(
    value: float | int | str | None, default: float = 0.0
) -> float:
    return (
        value
        if isinstance(value, (float, int)) and not isinstance(value, bool)
        else default
    )


def validate_values(csv_file: str, dtype_file: str, age: int) -> None:
    if not csv_file:
        raise ValueError("csv_file is empty or None")
    if not dtype_file:
        raise ValueError("dtype_file is empty or None")
    if age < 0:
        raise ValueError("age should not be negative")


def is_valid_file(path: str | Path) -> Path:
    result_path = Path(path)
    if not result_path.is_file():
        raise FileNotFoundError(f"The file {result_path} does not exist.")
    if result_path.stat().st_size == 0:
        raise ValueError(f"The file {result_path} is empty")
    return result_path


@retry(
    stop=stop_after_attempt(1),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError)),
)
def check_db_connection(engine: sa_engine.Engine) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.debug("Подкелючение к БД проверено")
    except Exception as e:
        logger.error(f"Ошибка подключения к БД. Детали: {e}", exc_info=True)
        raise ConnectionError(f"Не удалось подключиться к БД {e}") from e


def main():
    logger.info("Запуск ETL приложения")
    logger.debug("Получаю основные переменные")
    base_dir = conf.get("BASE_DIR")
    csv_file = conf.get("csv_file")
    db_url = URL.create(
        drivername=conf.get("DB_DRIVERNAME"),
        username=conf.get("DB_USER"),
        password=conf.get("DB_PASSWORD"),
        host=conf.get("DB_HOST"),
        port=conf.get("DB_PORT"),
        database=conf.get("DB_NAME"),
    )
    dtype_file = conf.get("DTYPE_SCHEMA_PATH")
    age = 30
    logger.debug("Проверяю корректность входных переменных")
    validate_values(csv_file, dtype_file, age)
    logger.debug("Проверяю корректность пути к csv")
    csv_path = is_valid_file(base_dir / csv_file)
    process_sample_data()
    process_csv_data(csv_path)
    logger.debug("Проверяю корректность пути к файлу dtype")
    dtype_path = is_valid_file(base_dir / dtype_file)
    logger.debug("Получаю словарь dtype")
    dtype_dict = get_dict(dtype_path)
    logger.debug(dtype_dict)
    logger.debug("Создаю соединение")
    engine = create_engine(db_url)
    check_db_connection(engine)
    logger.debug("Формирую контекст для ETL")
    ctx = m.ETLContext(engine=engine, csv_path=csv_path, dtype_dict=dtype_dict, age=age)
    logger.debug("Выполняю загрузку ETLContext")
    db_loader.loader(ctx)
    logger.debug("Завершаю соединение")
    engine.dispose()
    logger.info("Остановка ETL приложения")


if __name__ == "__main__":
    main()
