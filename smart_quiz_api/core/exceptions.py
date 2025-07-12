class PromptTemplateNotFound(Exception):
    """Raised when a quiz type template file is missing."""
    pass

class OpenAIResponseError(Exception):
    """Raised when OpenAI returns an invalid or incomplete response."""
    pass
