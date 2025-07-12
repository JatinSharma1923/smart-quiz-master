# smart_quiz_api/utils/__init__.py

# Logger utilities
from .logger import (
    setup_logger,
    logger,
    log_quiz_generation,
    log_quiz_completion,
    log_user_activity,
    log_system_health,
    log_error
)

# Text processing utilities
from .text_utils import (
    load_template,
    render_template,
    truncate_text,
    clean_text_for_quiz,
    extract_keywords,
    generate_text_hash,
    split_text_into_chunks,
    validate_quiz_text,
    format_quiz_question
)

# Authentication utilities
from .auth_utils import (
    verify_token,
    get_user_email,
    get_user_id,
    is_admin_user,
    validate_quiz_access,
    log_auth_attempt
)

# Retry utilities
from .retry_utils import (
    retry_openai_call,
    retry_with_custom_exception
)

# Decorators
from .decorators import (
    log_execution,
    timeit,
    safe_handler,
    cache_result,
    rate_limit,
    validate_input
)

# Export all utilities
__all__ = [
    # Logger
    "setup_logger",
    "logger",
    "log_quiz_generation",
    "log_quiz_completion",
    "log_user_activity",
    "log_system_health",
    "log_error",
    
    # Text processing
    "load_template",
    "render_template",
    "truncate_text",
    "clean_text_for_quiz",
    "extract_keywords",
    "generate_text_hash",
    "split_text_into_chunks",
    "validate_quiz_text",
    "format_quiz_question",
    
    # Authentication
    "verify_token",
    "get_user_email",
    "get_user_id",
    "is_admin_user",
    "validate_quiz_access",
    "log_auth_attempt",
    
    # Retry
    "retry_openai_call",
    "retry_with_custom_exception",
    
    # Decorators
    "log_execution",
    "timeit",
    "safe_handler",
    "cache_result",
    "rate_limit",
    "validate_input"
] 