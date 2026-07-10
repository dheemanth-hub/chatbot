from django.test import SimpleTestCase

from core_app.views import build_contextual_prompt, extract_llm_reply, get_fallback_reply


class ChatPromptTests(SimpleTestCase):
    def test_build_contextual_prompt_includes_previous_messages(self):
        history = [("user", "Hello"), ("bot", "Hi there")]
        prompt = build_contextual_prompt("How are you?", history)

        self.assertIn("user: Hello", prompt)
        self.assertIn("bot: Hi there", prompt)
        self.assertIn("How are you?", prompt)

    def test_get_fallback_reply_for_groq_questions(self):
        reply = get_fallback_reply("Explain Groq in 2 lines")

        self.assertIn("Groq", reply)
        self.assertIn("API", reply)

    def test_extract_llm_reply_supports_ollama_response(self):
        reply = extract_llm_reply({"response": "Hello from Ollama"})

        self.assertEqual(reply, "Hello from Ollama")
