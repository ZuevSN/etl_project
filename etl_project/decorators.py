# etl_project.decorators.py

import logging
import functools

logger = logging.getLogger(__name__)


# декоратор для изоляции процесса
# в случае ошибки падает только изолированный процесс
def isolated_process(process_name: str):
    def decorator(func: callable) -> callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> any:
            logger.info(f"Запуск процесса: {process_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Завершение процесса: {process_name}")
                return result
            except Exception as e:
                # logger.exception(f'{type(e).__name__}: {e}')
                logger.error(
                    f"Процесс {process_name} прерван.{type(e).__name__}: {e}. "
                    "Приложение продолжило работу"
                )
            return None

        return wrapper

    return decorator
