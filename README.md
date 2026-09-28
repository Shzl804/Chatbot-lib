# chatbot-lib (v1 core)

A beginner-friendly, provider-agnostic chatbot library. Give it a model
name and (if needed) an API key — it handles routing to the right
provider, keeps conversation memory, and supports streaming and fully
offline local models.

## Install

```bash
pip install -r requirements.txt
pip install -e .              # editable install of the package itself
pip install -e ".[openai]"    # + OpenAI support
pip install -e ".[anthropic]" # + Anthropic support
pip install -e ".[all]"       # + everything
```

## Quickstart

```python
from chatbot_lib import ChatBot

bot = ChatBot(model="gpt-4o-mini", api_key="sk-...")
print(bot.chat("Hello!"))
print(bot.chat("What did I just say?"))  # remembers the conversation
```

Fully offline, no API key, via a local [Ollama](https://ollama.com) model:

```python
bot = ChatBot(model="llama3")
print(bot.chat("Hello!"))
```

Streaming:

```python
for chunk in bot.stream("Tell me a short story."):
    print(chunk, end="", flush=True)
```

Saving / restoring a conversation:

```python
bot.save_session("chat.json")
bot.load_session("chat.json")
```

## How model routing works

`ChatBot` doesn't hardcode any provider. It looks at the prefix of the
`model` string and picks an adapter:

| Prefix                          | Provider    | Needs API key |
|----------------------------------|-------------|:---:|
| `gpt-`, `o1`, `o3`, `o4`, `chatgpt` | OpenAI      | yes |
| `claude-`                        | Anthropic   | yes |
| `llama`, `mistral`, `gemma`, `phi`, `qwen`, `deepseek` | Ollama (local) | no |

Don't see your model? Register your own provider without touching the
library's source:

```python
from chatbot_lib import register_provider
from chatbot_lib.providers.base import BaseProvider

class MyProvider(BaseProvider):
    def chat(self, messages, **kwargs): ...
    def stream_chat(self, messages, **kwargs): ...

register_provider(("gemini-",), MyProvider)
```

## Architecture

```
chatbot_lib/
├── core/
│   ├── chatbot.py      # ChatBot: the public class users import
│   └── session.py      # Session: conversation memory (get/save/load)
├── providers/
│   ├── base.py         # BaseProvider interface every adapter follows
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── ollama_provider.py
│   └── registry.py      # model-name -> provider-class lookup
└── exceptions.py
```

`ChatBot` never talks to an API directly — it asks the `Session` for
the message history, hands that to whichever `BaseProvider` subclass
matches the model name, and stores the reply back into the `Session`.
This is what makes swapping providers a one-line change (`model=`)
instead of a rewrite.

## Running tests

```bash
pip install -e ".[dev]"
pytest
```

## What's next (post-v1)

Per the planned build order: optional UI → tools/function calling →
RAG → MCP support. None of that is in this core v1 — it's just the
provider-agnostic chatbot + memory, kept intentionally small so it's
easy to read end to end before adding more.
