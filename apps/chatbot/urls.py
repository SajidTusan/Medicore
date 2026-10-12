from django.urls import path
from .views import chat_api, chatbot_page

app_name = "chatbot"

urlpatterns = [
    path("api/", chat_api, name="api"),
    path("", chatbot_page, name="page"),
]
