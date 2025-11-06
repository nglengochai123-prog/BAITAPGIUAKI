from django.urls import path
from . import views

urlpatterns = [
    path('tinhluong/', views.payroll_management_view, name='payroll_management_view'),
]