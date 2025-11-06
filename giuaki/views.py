from django.shortcuts import render, redirect
# Thêm các import này
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login  # Đổi tên để tránh trùng lặp
from django.contrib.auth.forms import AuthenticationForm
def welcome_view(request):
    return render(request, 'base.html')
def welcome_view_manager(request):
    return render(request, 'basemanager.html')
def welcome_view_employee(request):
    return render(request, 'baseemployee.html')
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)

                if user.groups.filter(name='HR').exists():
                    return redirect('welcome_hr')  # Đi đến trang HR

                elif user.groups.filter(name='Quản lý phòng ban').exists():
                    return redirect('welcome_manager')  # Đi đến trang Quản lý

                else:
                    # Mặc định là 'Nhân viên'
                    return redirect('welcome_employee')  # Đi đến trang Nhân viên
    else:
        # Nếu là request GET, chỉ hiển thị form login
        form = AuthenticationForm()

    # Nếu login thất bại (POST) hoặc là (GET), hiển thị lại trang login
    return render(request, 'login.html', {'form': form})