# etl_project.models.py

from dataclasses import dataclass
from sqlalchemy.engine import Engine
from typing import Optional

# структура для хранения данных контекста ETL
@dataclass
class ETLContext:
    # 1 Обязательные поля для контекста
    engine: Engine
    csv_path: str
    dtype_dict: dict
    age: int = 30
    multiplier: float = 0.2
    # 2 Опциональные поля для будующего расширения(не ломают старый код)
    # нужно им сделать значение по умолчанию и тогда для старых объектов
    # не произведет поломку. Лучше сделать значение None
    # для примера
    additional_path: Optional[str] = None