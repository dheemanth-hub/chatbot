import json
import os
import re
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import ChatMessage

def get_llm_backend_config():
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()
    if provider == "ollama":
        return {
            "provider": "ollama",
            "url": os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/"),
            "model": os.environ.get("OLLAMA_MODEL", "llama3.2"),
        }

    return {
        "provider": "groq",
        "url": os.environ.get("GROQ_URL", "https://api.groq.dev/v1").rstrip("/"),
        "model": os.environ.get("GROQ_MODEL", "gpt-4o-mini"),
        "api_key": os.environ.get("GROQ_API_KEY"),
    }


def build_contextual_prompt(message, history):
    history_text = "\n".join(f"{sender}: {text}" for sender, text in history[-6:])
    if history_text:
        return f"Conversation history:\n{history_text}\n\nUser: {message}"
    return f"User: {message}"


def get_fallback_reply(message):
    text = (message or "").strip().lower()
    if "groq" in text:
        return (
            "Groq is an API for calling large language models from the cloud. "
            "It lets your app generate text responses by sending prompts to a hosted LLM."
        )
    if "rag" in text:
        return (
            "RAG stands for Retrieval-Augmented Generation. It is a way to improve AI answers by first retrieving relevant information from a knowledge source and then using that information to generate a better response."
        )
    if "hello" in text or "hi" in text:
        return "Hello! I can help explain Groq, RAG, or answer simple questions."
    if "ai" in text or "artificial intelligence" in text:
        return "AI means artificial intelligence. It is the ability of machines to perform tasks that usually need human thinking, such as understanding language, recognizing patterns, and making decisions."
    if "how" in text or "what" in text or "why" in text:
        return "I can explain common AI topics like Groq and RAG in simple terms."
    return f"I can help with that. Your message was: {message}."


@login_required
def chat_view(request):
    messages = ChatMessage.objects.order_by('created_at')[:100]
    return render(request, "core/chat.html", {"messages": messages})


def logout_view(request):
    logout(request)
    return redirect('login')


def profile_redirect(request):
    return redirect('chat')


@csrf_exempt
@require_POST
@login_required
def chat_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"reply": "Please send valid JSON."})

    prompt = data.get("message", "")

    if not prompt.strip():
        return JsonResponse({"reply": "Please type a message."})

    history = list(ChatMessage.objects.order_by("created_at").values_list("sender", "text"))
    ChatMessage.objects.create(sender="user", text=prompt)

    contextual_prompt = build_contextual_prompt(prompt, history)

    try:
        backend = get_llm_backend_config()
        print("LLM BACKEND CONFIG:", backend)  # TEMP DEBUG - remove once fixed

        if backend["provider"] == "ollama":
            response = requests.post(
                f"{backend['url']}/api/generate",
                json={
                    "model": backend["model"],
                    "prompt": contextual_prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            reply = extract_llm_reply(result) or "No response from Ollama"
        else:
            if not backend["api_key"]:
                raise RuntimeError("Groq API key is not configured")

            response = requests.post(
                f"{backend['url']}/{backend['model']}/generate",
                headers={
                    "Authorization": f"Bearer {backend['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": contextual_prompt,
                    "temperature": 0.7,
                    "max_output_tokens": 256,
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            reply = extract_llm_reply(result) or "No response from Groq"
    except Exception as e:
        print("LLM CALL FAILED:", repr(e))  # TEMP DEBUG - remove once fixed
        reply = get_fallback_reply(prompt)

    ChatMessage.objects.create(sender="bot", text=reply)
    return JsonResponse({"reply": reply})


def extract_llm_reply(response_json):
    if not isinstance(response_json, dict):
        return None

    if "response" in response_json:
        response_text = response_json["response"]
        if isinstance(response_text, str):
            return response_text

    if "message" in response_json:
        message = response_json["message"]
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content

    if "output" in response_json:
        output = response_json["output"]
        if isinstance(output, str):
            return output
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return first.get("content") or first.get("text")

    if "choices" in response_json:
        choices = response_json["choices"]
        if isinstance(choices, list) and choices:
            first_choice = choices[0]
            if isinstance(first_choice, dict):
                if "text" in first_choice:
                    return first_choice["text"]
                message = first_choice.get("message")
                if isinstance(message, dict):
                    return message.get("content")

    if "results" in response_json:
        results = response_json["results"]
        if isinstance(results, list) and results:
            first_result = results[0]
            if isinstance(first_result, dict):
                return first_result.get("output") or first_result.get("text")

    return None