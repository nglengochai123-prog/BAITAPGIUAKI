from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.candidate_apply, name='candidate_apply'),
]