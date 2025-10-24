from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome_view'),
    path('apply/', views.candidate_apply, name='candidate_apply'),
    path('tuyendung/', views.tuyendung, name='tuyendung'),
    path('tuyendung/baidang/', views.baidang_list, name='baidang_list'),
    path('tuyendung/quanly/', views.quanly_tuyendung, name='quanly_tuyendung'),
]