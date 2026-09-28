"""Custom exceptions for chatbot_lib.

Keeping these in one place means users can do:
    from chatbot_lib import ProviderError
and catch exactly what they need, instead of guessing which
underlying SDK's exception type might be raised.
"""


class ChatbotLibError(Exception):
    """Base class for every exception raised by this library."""


class UnsupportedModelError(ChatbotLibError):
    """Raised when the model name doesn't match any known provider."""


class ProviderError(ChatbotLibError):
    """Raised when a provider's underlying API call fails."""


class MissingDependencyError(ChatbotLibError):
    """Raised when an optional provider's SDK isn't installed.

    Example: using model="gpt-4o" without `pip install chatbot-lib[openai]`.
    """
