from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("", lambda request: redirect('polls/', permanent=False)),
    path("polls/", include("django.contrib.auth.urls")),
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    path("", include("allauth.urls")),
]