
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services import handle_message

@login_required
def chatbot_page(request):
    return render(request, "chatbot/chat.html")

@login_required
@require_POST
def chat_api(request):
    try:
        payload = json.loads(request.body or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"reply": "Invalid request. Please try again.", "doctors": []},
            status=400,
        )

    message = payload.get("message", "")

    if not isinstance(message, str) or len(message) > 500:
        return JsonResponse(
            {"reply": "Message must be under 500 characters.", "doctors": []},
            status=400,
        )

    try:
        result = handle_message(message)
    except Exception:
        return JsonResponse(
            {
                "reply": (
                    "Sorry, I couldn't process that request. "
                    "Please try again or use the Doctors page."
                ),
                "doctors": [],
            },
            status=200,
        )

    return JsonResponse(result)
