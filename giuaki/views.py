from django.shortcuts import render, redirect

def welcome_view(request):
    # Hàm render sẽ tìm và tải base.html lên
    return render(request, 'base.html')

def welcome_view_manager(request):
    return render(request, 'basemanager.html')

def welcome_view_employee(request):
    return render(request, 'baseemployee.html')

def login(request):
    return render(request, 'login.html')