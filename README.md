# yourlib (working name)

A lightweight, provider-agnostic Python library for building chatbots. Give it a model name and an API key — it handles the rest: talking to the right provider, managing conversation history, and (optionally) giving you a ready-made UI.

Inspired by tools like LiteLLM and LangChain, but built to stay minimal, beginner-friendly, and easy to extend — including first-class support for local/offline models.

---

## Why this exists

Every LLM provider (OpenAI, Anthropic, Gemini, local models via Ollama) has a different API shape. Most existing libraries either lock you into one provider or come with heavy dependencies and a steep learning curve. This library aims to:

- Work with any supported provider using the *same* code
- Stay lightweight by default (core has almost no dependencies)
- Offer an optional built-in UI, but never force it
- Grow from "simple chatbot" to "RAG + tools + MCP agent" without breaking the simple use case

---

## Architecture

```
User's app
    |
    |  model="gpt-4o", api_key="..."
    v
+----------------------------------------------------+
|                     yourlib (core)                  |
|                                                        |
|   +--------------------------------------------+    |
|   |              ChatBot class                  |    |
|   |   public interface, takes model + api_key   |    |
|   +--------------------------------------------+    |
|                       |                             |
|   +-------------------+------------------------+    |
|   |               Core engine                   |   |
|   |  +----------------+   +-------------------+ |   |
|   |  | Provider router |   | Session manager   | |   |
|   |  | model -> adapter |   | history + memory  | |   |
|   |  +----------------+   +-------------------+ |   |
|   +----------------------------------------------+   |
|                       |                             |
|   +-------------------+------------------------+    |
|   |             Provider adapters                |   |
|   |   [ OpenAI ]   [ Anthropic ]   [ Gemini ]    |   |
|   +----------------------------------------------+   |
+----------------------------------------------------+
                       |
                       v
              Real LLM provider APIs
```

**Flow of a single message:**
1. User calls `bot.send("hello")` on the `ChatBot` object.
2. `ChatBot` hands the message to the **session manager**, which appends it to conversation history.
3. The **provider router** looks at the model name (e.g. `"claude-sonnet-5"`) and picks the matching adapter.
4. The adapter converts the standardized message list into that provider's exact API format, sends the request, and normalizes the response back.
5. `ChatBot` returns a clean string (or structured object) to the user, and the session manager stores the reply in history.

---

## File structure (v1)

```
yourlib/
├── yourlib/
│   ├── __init__.py
│   ├── chatbot.py            # ChatBot class (public interface)
│   ├── router.py             # Provider router — maps model name to adapter
│   ├── session.py            # Session/history manager
│   ├── config.py             # Pydantic config & settings validation
│   ├── exceptions.py         # Unified error types across providers
│   └── providers/
│       ├── __init__.py
│       ├── base.py           # BaseProvider abstract class
│       ├── openai_provider.py
│       ├── anthropic_provider.py
│       └── gemini_provider.py
│
├── ui/                        # optional, only loaded if installed
│   ├── __init__.py
│   └── streamlit_app.py       # basic ready-made chat UI
│
├── tests/
│   ├── test_router.py
│   ├── test_session.py
│   └── test_providers.py
│
├── examples/
│   ├── basic_usage.py
│   └── custom_ui_example.py
│
├── requirements.txt
├── pyproject.toml             # packaging config (for pip install)
├── README.md
└── .env.example
```

---

## What's needed to build v1

**1. Core interface**
- `ChatBot(model, api_key, **config)` class
- `.send(message)` method for single-turn or multi-turn chat
- Clean error messages instead of raw provider tracebacks

**2. Provider router**
- Simple name-based matching (`gpt-*` → OpenAI, `claude-*` → Anthropic, `gemini-*` → Gemini)
- Easy to register a new provider without touching core code

**3. Provider adapters**
- `BaseProvider` abstract class defining `.chat(messages, **kwargs)`
- One adapter class per provider, each normalizing request/response format

**4. Session manager**
- Stores conversation as `[{"role": ..., "content": ...}, ...]`
- Supports resetting, exporting, and re-loading history

**5. Config & validation**
- Pydantic models to validate API keys, model names, and settings
- `.env` support so users don't hardcode API keys

**6. Packaging**
- `pyproject.toml` so it installs via `pip install yourlib`
- Optional extras: `pip install yourlib[ui]` for the built-in UI

**7. Basic optional UI**
- A Streamlit (or Gradio) chat interface that wraps `ChatBot`
- Not loaded unless the user installs the `[ui]` extra
- Core `ChatBot` stays UI-agnostic so users can plug in their own frontend

**8. Tests**
- Unit tests per adapter (mocked API calls, no real network needed)
- Router and session manager tests

---

## v2 roadmap (planned, not in v1)

- **Tool / function calling** — unified interface for defining tools the model can call, normalized across providers
- **RAG support** — a `yourlib.rag` module for embeddings + vector store integration (so users can plug in documents for the chatbot to reference)
- **MCP (Model Context Protocol) support** — connect the chatbot to external MCP servers for tools, data, and actions
- **Streaming responses** — token-by-token output support across all providers
- **Local/offline models** — first-class support for Ollama / llama.cpp so the library works without any paid API
- **Cost & token tracking** — show estimated cost per call, useful for learning and budgeting
- **More providers** — Mistral, Cohere, local Hugging Face models, etc.
