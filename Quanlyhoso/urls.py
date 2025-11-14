from django.urls import path
from . import views

urlpatterns = [
    path('my-profile/', views.my_profile, name='profile'),
    path('profile/update/', views.request_profile_update, name='request_profile_update'),
    path('hr/requests/', views.hr_request_list, name='hr_request_list'),
    path('hr/requests/<int:pk>/', views.hr_request_detail, name='hr_request_detail'),
    path('hr/employees/', views.employee_list_view, name='employee_list'),
    path('training/request/', views.request_training_view, name='request_training'),
    path('hr/profile/<str:pk>/', views.hr_view_employee_profile, name='hr_view_profile'),
    path('hr/employees/add/', views.add_employee_view, name='add_employee'),
    path('hr/employees/edit/<str:pk>/', views.edit_employee_view, name='edit_employee'),
    path('hr/employees/delete/<str:pk>/', views.delete_employee_view, name='delete_employee'),
    path('hr/training-requests/', views.hr_training_list, name='hr_training_list'),
    path('hr/training-requests/<int:pk>/', views.hr_training_detail, name='hr_training_detail'),
]
