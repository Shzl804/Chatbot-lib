import pytest

from chatbot_lib.exceptions import UnsupportedModelError
from chatbot_lib.providers.anthropic_provider import AnthropicProvider
from chatbot_lib.providers.ollama_provider import OllamaProvider
from chatbot_lib.providers.openai_provider import OpenAIProvider
from chatbot_lib.providers.registry import get_provider_class


@pytest.mark.parametrize(
    "model,expected",
    [
        ("gpt-4o", OpenAIProvider),
        ("gpt-3.5-turbo", OpenAIProvider),
        ("o3-mini", OpenAIProvider),
        ("claude-sonnet-4-6", AnthropicProvider),
        ("llama3", OllamaProvider),
        ("mistral-7b", OllamaProvider),
    ],
)
def test_known_models_map_to_expected_provider(model, expected):
    assert get_provider_class(model) is expected


def test_unknown_model_raises():
    with pytest.raises(UnsupportedModelError):
        get_provider_class("some-made-up-model-xyz")
