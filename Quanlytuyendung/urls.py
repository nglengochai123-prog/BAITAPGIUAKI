from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('tuyendung/apply/', views.candidate_apply, name='candidate_apply'),
    path('tuyendung/', views.recruitment_home, name='recruitment_home'),
    path('tuyendung/baidangtuyendung/', views.all_job_postings, name='all_job_postings'),
    path('tuyendung/quanly/', views.quanly_tuyendung, name='quanly_tuyendung'),
    path('tuyendung/create/', views.create_recruitment_post, name='create_recruitment_post'),
]