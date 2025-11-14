from django.urls import path
from . import views

urlpatterns = [
    path('project-list/', views.project_list, name='project_list'),
    path('project-list/create/', views.project_create, name='project_create'),
    path('project-list/edit/<int:pk>/', views.project_edit, name='project_edit'),
    path('criteria-list/', views.criteria_list, name='criteria_list'),
    path('criteria-list/create/', views.criteria_create, name='criteria_create'),
    path('reward-list/', views.reward_list, name='reward_list'),
    path('reward-suggest-list/', views.reward_suggest_list, name='reward_suggest_list'),
    path('reward-suggest-list/create', views.reward_suggest_form, name='reward_suggest_form'),
    path('reward-announce-list', views.reward_announce_list, name='reward_announce_list'),
]

