
import json
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .flows import get_start_options
from .services import handle_message

@login_required
def chatbot_page(request):
    return render(
        request,
        "chatbot/chat.html",
        {
            "ai_enabled": bool(getattr(settings, "GEMINI_API_KEY", "")),
            "guided_options": get_start_options(request.user.role),
        },
    )

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

    if not isinstance(payload, dict):
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

    message = message.strip()
    if not message:
        return JsonResponse(
            {"reply": "Please type a message.", "doctors": []},
            status=400,
        )

    rate_key = f"chatbot:user:{request.user.pk}"
    request_count = cache.get(rate_key, 0)
    if request_count >= 30:
        return JsonResponse(
            {
                "reply": "You've reached the chat limit for this hour. Please try again later.",
                "doctors": [],
            },
            status=429,
        )
    if request_count:
        cache.incr(rate_key)
    else:
        cache.set(rate_key, 1, timeout=60 * 60)

    try:
        result = handle_message(message, user=request.user)
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
