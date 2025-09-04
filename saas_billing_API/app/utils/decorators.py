import time
import functools
import logging

logger = logging.getLogger(__name__)

def log_execution_time(func):
    """
    Decorator that logs execution time of async functions.

    - Logs duration in ms using the logger.
    - Adds "execution_time_ms" to results if they are dicts or Pydantic models.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = round((time.time() - start) * 1000)


        logger.info(f"{func.__name__} executed in {duration} ms")
         
        if hasattr(result, "dict"):
            result_dict = result.dict()
            result_dict["execution_time_ms"] = duration
            return result_dict
        elif isinstance(result, dict):
            result["execution_time_ms"] = duration
            return result
        else:
            return result

    return wrapper

