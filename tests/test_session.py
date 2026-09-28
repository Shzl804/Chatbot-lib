import json
import os
import tempfile

from chatbot_lib.core.session import Session


def test_add_messages():
    s = Session()
    s.add_user_message("hi")
    s.add_assistant_message("hello")
    assert s.get_messages() == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]
    assert len(s) == 2


def test_max_history_trims_oldest_turns():
    s = Session(max_history=1)  # keep only 1 turn pair = 2 messages
    for i in range(3):
        s.add_user_message(f"u{i}")
        s.add_assistant_message(f"a{i}")
    assert s.get_messages() == [
        {"role": "user", "content": "u2"},
        {"role": "assistant", "content": "a2"},
    ]


def test_clear():
    s = Session()
    s.add_user_message("hi")
    s.clear()
    assert len(s) == 0


def test_save_and_load_roundtrip():
    s = Session(system_prompt="be nice")
    s.add_user_message("hi")
    s.add_assistant_message("hello")

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "session.json")
        s.save(path)

        with open(path) as f:
            raw = json.load(f)
        assert raw["system_prompt"] == "be nice"

        loaded = Session.load(path)
        assert loaded.system_prompt == "be nice"
        assert loaded.get_messages() == s.get_messages()
