"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.urls import include
from .views import health_check

urlpatterns = [
    path("health/", health_check, name="health"),
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.home_urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("doctors/", include("apps.doctors.urls")),
    path("nurses/", include("apps.nurses.urls")),
    path("schedule/", include("apps.schedule_manager.urls")),
    path("patients/", include("apps.patients.urls")),
    path("appointments/",include("apps.appointments.urls"),),
    path("medical-records/",include("apps.medical_records.urls"),),
    path("pharmacy/",include("apps.pharmacy.urls"),),
    path("billing/",include("apps.billing.urls"),),
    path("notifications/",include("apps.notifications.urls"),),
    path("search/",include("apps.search.urls"),),
    path("chatbot/", include("apps.chatbot.urls")),
]
