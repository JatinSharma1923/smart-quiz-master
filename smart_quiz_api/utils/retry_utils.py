# smart_quiz_api/utils/retry_utils.py

import functools
from typing import Callable, Any, TypeVar, Union, Type
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from smart_quiz_api.utils.logger import logger

# Type variable for function return type
T = TypeVar('T')

def retry_openai_call(
    max_attempts: int = 3,
    min_wait: float = 2.0,
    max_wait: float = 10.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying OpenAI API calls with exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        @retry(
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            stop=stop_after_attempt(max_attempts),
            reraise=True
        )
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"🔁 Retrying {func.__name__} due to error: {str(e)}")
                raise
        return wrapper
    return decorator

def retry_with_custom_exception(
    exception_types: Union[Type[Exception], tuple[Type[Exception], ...]],
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 5.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying functions with custom exception types."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        @retry(
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            stop=stop_after_attempt(max_attempts),
            retry=retry_if_exception_type(exception_types),
            reraise=True
        )
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except exception_types as e:  # type: ignore
                logger.warning(f"🔁 Retrying {func.__name__} due to {type(e).__name__}: {str(e)}")
                raise
        return wrapper
    return decorator
