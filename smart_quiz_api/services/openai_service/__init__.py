"""
smart_quiz_api.services.openai_service

This package provides all AI-related service utilities, including:
- OpenAI client initialization and SDK compatibility
- Prompt rendering and trimming
- Redis caching
- Retry logic and fallback handling
- Task-specific AI logic like classification, explanation, tagging, grading
"""

# === Client Layer (SDK handling, token estimation, fallback) ===
from .ai_client import (
    openai_client,
    use_new_openai,
    estimate_tokens,
    get_valid_model,
    fallback_response,
    trim_prompt_to_fit,
    call_openai,
)

# === Prompt Templates and Renderer ===
from .prompt import (
    load_prompt_template,
    render_prompt,
)

# === Caching Layer ===
from .cache import (
    get_cached_response,
    set_cached_response,
    get_cache_key,
)

# === Core AI Task Logic ===
from .ai_tasks import(
    safe_openai_chat,
    classify_topic,
    generate_tags,
    generate_explanation,
    grade_answer,
    estimate_confidence,
    check_openai_health,
    parse_ai_quiz_response,
)

# === Public Export Symbols ===
__all__ = [
    # ai_client.py
    "openai_client",
    "use_new_openai",
    "estimate_tokens",
    "get_valid_model",
    "fallback_response",
    "trim_prompt_to_fit",
    "call_openai",

    # prompt.py
    "load_prompt_template",
    "render_prompt",

    # cache.py
    "get_cached_response",
    "set_cached_response",
    "get_cache_key",

    # ai_tasks.py
    "safe_openai_chat",
    "classify_topic",
    "generate_tags",
    "generate_explanation",
    "grade_answer",
    "estimate_confidence",
    "check_openai_health",
    "parse_ai_quiz_response",
]
