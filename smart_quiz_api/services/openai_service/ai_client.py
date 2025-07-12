import logging
import tiktoken

from smart_quiz_api.core.exceptions import OpenAIResponseError
from smart_quiz_api.config import settings
from smart_quiz_api.constants import DEFAULT_MODEL

# === Logger Setup ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === Load OpenAI API Key ===
config_api_key = settings.openai_api_key

if not config_api_key:
    raise ValueError("OPENAI_API_KEY must be set in environment or .env")

# === OpenAI SDK Compatibility Layer ===
try:
    # New OpenAI SDK (v1.x)
    from openai import OpenAI
    openai_client = OpenAI(api_key=config_api_key)
    use_new_openai = True
    logger.info("✅ Using OpenAI SDK v1.x client.")
except ImportError:
    # Legacy OpenAI SDK (v0.x)
    import openai
    openai.api_key = config_api_key
    openai_client = openai
    use_new_openai = False
    logger.info("⚠️  Using legacy OpenAI SDK v0.x client.")

# === Token Estimation ===
def estimate_tokens(prompt: str, model: str = DEFAULT_MODEL) -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(prompt))

# === Model Validation ===
def get_valid_model(requested_model: str) -> str:
    supported_models = ["gpt-4", "gpt-4o", "gpt-3.5-turbo"]
    return requested_model if requested_model in supported_models else "gpt-3.5-turbo"

# === Fallback Response Handler ===
def fallback_response(prompt: str) -> str:
    logger.warning("⚠️ Using fallback response due to OpenAI failure.")
    return "We're currently experiencing technical difficulties. Please try again later."

# === Prompt Trimmer (Optional Helper) === 
def trim_prompt_to_fit(prompt: str, max_tokens: int, model: str = DEFAULT_MODEL) -> str:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")

    encoded = encoding.encode(prompt)
    if len(encoded) > max_tokens:
        trimmed = encoded[:max_tokens]
        return encoding.decode(trimmed)
    return prompt

def call_openai(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 700,
    temperature: float = 0.7,
) -> str:
    try:
        if use_new_openai:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""

        else:
            # For legacy OpenAI SDK (v0.x)
            response = openai.ChatCompletion.create(  # type: ignore
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response["choices"][0]["message"]["content"]  # type: ignore
            return content.strip() if content else ""  # type: ignore

    except Exception as e:
        logger.error(f"[OpenAI API Error] {e}")
        raise OpenAIResponseError(str(e))

# === Public Symbols for Import ===
__all__ = [
    "openai_client",
    "use_new_openai",
    "estimate_tokens",
    "get_valid_model",
    "fallback_response",
    "trim_prompt_to_fit",
    "call_openai"
]
