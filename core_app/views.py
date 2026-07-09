import json
import re
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import ChatMessage

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def build_contextual_prompt(message, history):
    history_text = "\n".join(f"{sender}: {text}" for sender, text in history[-6:])
    if history_text:
        return f"Conversation history:\n{history_text}\n\nUser: {message}"
    return f"User: {message}"


def get_fallback_reply(message):
    text = (message or "").strip().lower()
    if "ollama" in text:
        return (
            "Ollama is a tool for running local AI models on your own machine. "
            "It lets you chat with models locally without sending everything to the cloud."
        )
    if "hello" in text or "hi" in text:
        return "Hello! I can help explain Ollama or answer simple questions."
    return "I can help explain Ollama or answer simple questions."


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
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3.2",
                "prompt": contextual_prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        reply = result.get("response", "No response from Ollama")
    except Exception:
        reply = get_fallback_reply(prompt)

    ChatMessage.objects.create(sender="bot", text=reply)
    return JsonResponse({"reply": reply})