from django.urls import path
from . import views

urlpatterns = [
    path('tinhluong/', views.payroll_management_view, name='payroll_management_view'),
    path('detail/<int:entry_id>/', views.payroll_detail_view, name='payroll_detail_view'),
    path('export-excel/<int:period_id>/', views.export_payroll_excel, name='export_payroll_excel'),
]
