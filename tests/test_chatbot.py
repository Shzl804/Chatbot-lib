from chatbot_lib import ChatBot
from chatbot_lib.providers.base import BaseProvider


class FakeProvider(BaseProvider):
    """A provider that echoes input instead of calling a real API.
    Used so tests never need network access or a real API key.
    """

    def chat(self, messages, **kwargs):
        last_user = messages[-1]["content"]
        return f"echo: {last_user}"

    def stream_chat(self, messages, **kwargs):
        for word in self.chat(messages).split():
            yield word + " "


def make_bot(**kwargs):
    return ChatBot(model="fake-model", provider=FakeProvider, **kwargs)


def test_chat_returns_reply_and_remembers_it():
    bot = make_bot()
    reply = bot.chat("hi there")
    assert reply == "echo: hi there"
    assert len(bot.session) == 2  # user turn + assistant turn


def test_system_prompt_is_included_but_not_stored_in_session():
    bot = make_bot(system_prompt="be concise")
    bot.chat("hi")
    # system prompt lives on the session config, not as a stored turn
    assert bot.session.system_prompt == "be concise"
    assert all(m["role"] != "system" for m in bot.session.get_messages())


def test_stream_yields_chunks_and_saves_full_reply():
    bot = make_bot()
    chunks = list(bot.stream("hello world"))
    assert "".join(chunks).strip() == "echo: hello world"
    assert bot.session.get_messages()[-1]["content"].strip() == "echo: hello world"


def test_reset_clears_history_but_keeps_system_prompt():
    bot = make_bot(system_prompt="stay on topic")
    bot.chat("hi")
    bot.reset()
    assert len(bot.session) == 0
    assert bot.session.system_prompt == "stay on topic"


def test_max_history_is_passed_through():
    bot = make_bot(max_history=1)
    bot.chat("first")
    bot.chat("second")
    # only the most recent turn pair should remain
    assert len(bot.session) == 2
    assert bot.session.get_messages()[0]["content"] == "second"
