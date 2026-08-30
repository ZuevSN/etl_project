# config.py
from pathlib import Path
from dotenv import dotenv_values
import logging
from typing import Dict, Any

# один рутовый логгер
logger = logging.getLogger()
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULTS_CONFIG = {
    "BASE_DIR": Path(BASE_DIR),
    "LOG_FILE": Path(BASE_DIR / "app.log"),
    "ENV_FILE": Path(BASE_DIR / ".env"),
    "FORMAT_LOG": "%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    "DATE_FMT": "%Y-%m-%d %H:%M:%S",
    "LEVEL_LOG": "INFO",  # DEBUG  10, INFO 20, WARNING 30, ERROR 40, CRITICAL 50
}


class AppConfig:
    def __init__(self, defaults: Dict[str, Any] = None, protected: set = None):
        """По умолчанию защищенные переменные BASE_DIR, LOG_FILE и ENV_FILE"""
        self.logger = logger
        self._params = {}
        self._defaults = DEFAULTS_CONFIG
        self._defaults.update(defaults or {})
        self._setup_logging_stream()
        self._create_path(self._defaults["BASE_DIR"])
        self._create_path(self._defaults["LOG_FILE"].parent)
        self._protected = {"BASE_DIR", "LOG_FILE", "ENV_FILE"}
        self._build_protected(protected)
        self._load_config()

    def _build_protected(self, protected):
        """По умолчанию защищенные переменные BASE_DIR и LOG_FILE"""
        if protected:
            self._protected = self._protected.union(protected)
        bad_keys = self._protected.difference(self._defaults.keys())
        if bad_keys:
            self.logger.warning(
                f"Не найдены защищенные параметры конфигурации: {bad_keys}"
            )

    """Задаю настройки логгирования если не заданы в основном приложении"""

    def _setup_logging_stream(self):
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter(self._defaults["FORMAT_LOG"])
            )
            self.logger.addHandler(console_handler)
            self.logger.setLevel(self._defaults["LEVEL_LOG"])

    def _setup_logging_file(self):
        if not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            file_handler = logging.FileHandler(
                filename=self._defaults["LOG_FILE"],
                encoding="utf-8",
            )
            file_handler.setFormatter(logging.Formatter(self._defaults["FORMAT_LOG"]))
            self.logger.addHandler(file_handler)

    def _create_path(self, path: Path):
        """Безопасно создаю пути"""
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Ошибка при создании директорий {path}: {str(e)}")
            raise

    def _load_config(self):
        self.logger.info("Начата сборка конфигурации")
        """Загружаю настройки из основного приложения (по умолчанию)"""
        self._params.update(self._defaults)

        self.logger.debug("В параметры конфигурации добавлены значения по умолчанию")
        """Загружаю настройки из env при наличии"""
        if Path(self._params.get("ENV_FILE")).exists():
            env_vars = dotenv_values(self._params.get("ENV_FILE"))
            for key in self._protected:
                env_vars.pop(key, None)
            self._params.update(env_vars)
            self.logger.debug(
                "В параметры конфигурации добавлены значения из файла настроек"
            )
        else:
            self.logger.warning(
                f"Не обнаружен файл настроек по пути {self._params.get('ENV_FILE')}. "
                "Будут использованы значения по умолчанию"
            )
        self.logger.debug(f"Параметры конфигурации: {list(self._params.keys())}")
        self.logger.info("Конфигурация подготовлена.")
        self.logger.info("Программа выполняется")
        self.logger.setLevel(self._params["LEVEL_LOG"])

    def set(self, key: str, value: Any):
        if key in self._protected:
            self.logger.warning(
                f"Попытка изменить защищиенный параметр конфигурации{key}."
            )
            return
        """Возможно стоит сделать дозапись env"""
        if key in self._params:
            self.logger.debug(f"Перезапись параметра {key} в конфигурации")
        else:
            self.logger.debug(f"В конфигурацию добавлен параметр {key}")
        self._params[key] = value

    def get(self, key: str, default=None):
        return self._params.get(key, default)
