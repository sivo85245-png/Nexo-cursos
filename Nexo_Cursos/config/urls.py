from django.contrib import admin
from django.urls import path, include

urlpatterns = [path('gestao-tecnica/', admin.site.urls), path('', include('academy.urls'))]
