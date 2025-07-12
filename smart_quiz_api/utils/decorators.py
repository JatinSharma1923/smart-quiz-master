# smart_quiz_api/utils/decorators.py

import functools
import time
from typing import Callable, Any, TypeVar, Optional
from smart_quiz_api.utils.logger import logger

T = TypeVar('T')

def log_execution(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log function execution."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        logger.info(f"▶️ Executing: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"✅ Done: {func.__name__}")
        return result
    return wrapper

def timeit(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"⏱️ {func.__name__} took {duration:.2f}s")
        return result
    return wrapper

def safe_handler(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """Decorator to safely handle exceptions and return None on error."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"❌ Exception in {func.__name__}: {str(e)}")
            return None
    return wrapper

def cache_result(cache_duration: int = 300):
    """Decorator to cache function results for a specified duration."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: dict[str, tuple[T, float]] = {}
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check if result is cached and not expired
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < cache_duration:
                    logger.debug(f"📋 Cache hit for {func.__name__}")
                    return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            logger.debug(f"💾 Cached result for {func.__name__}")
            return result
        return wrapper
    return decorator

def rate_limit(max_calls: int = 100, time_window: int = 3600):
    """Decorator to implement rate limiting."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        call_history: list[float] = []
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_time = time.time()
            
            # Remove old calls outside the time window
            call_history[:] = [call_time for call_time in call_history 
                             if current_time - call_time < time_window]
            
            # Check if rate limit exceeded
            if len(call_history) >= max_calls:
                logger.warning(f"🚫 Rate limit exceeded for {func.__name__}")
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {time_window}s")
            
            # Add current call to history
            call_history.append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_input(*required_params: str):
    """Decorator to validate required parameters."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Check if all required parameters are provided
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"Missing required parameter: {param}")
                if kwargs[param] is None or kwargs[param] == "":
                    raise ValueError(f"Parameter {param} cannot be empty")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

