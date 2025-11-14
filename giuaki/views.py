from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
# --- THÊM CÁC IMPORT NÀY ---
from django.contrib.auth.decorators import login_required, user_passes_test

# ===================================================================
# --- CÁC HÀM KIỂM TRA QUYỀN (chúng ta đã làm ở bước trước) ---
# ===================================================================

def is_employee(user):
    """
    Kiểm tra xem user có phải là NHÂN VIÊN không
    (Đã đăng nhập VÀ KHÔNG thuộc nhóm HR/Quản lý)
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return False
    # Kiểm tra có thuộc nhóm cấp cao không
    is_manager_or_hr = user.groups.filter(name__in=['HR', 'Quản lý phòng ban']).exists()
    # Trả về True NẾU KHÔNG thuộc nhóm HR/Quản lý
    return not is_manager_or_hr

def is_manager_or_hr(user):
    """
    Kiểm tra xem user có phải là HR hoặc QUẢN LÝ không
    (Đúng theo logic 'login' của bạn)
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True # Superuser có mọi quyền
    return user.groups.filter(name__in=['HR', 'Quản lý phòng ban']).exists()


# ===================================================================
# --- CÁC VIEW WELCOME ĐÃ ĐƯỢC BẢO VỆ ---
# ===================================================================

# (Giả sử view này là 'welcome_hr' trỏ đến base.html của HR)
@user_passes_test(is_manager_or_hr, login_url='/login/')
def welcome_view(request):
    return render(request, 'base.html')

@user_passes_test(is_manager_or_hr, login_url='/login/')
def welcome_view_manager(request):
    return render(request, 'basemanager.html')

@user_passes_test(is_employee, login_url='/login/')
def welcome_view_employee(request):
    return render(request, 'baseemployee.html')

# ===================================================================
# --- VIEW LOGIN (Giữ nguyên, không cần sửa) ---
# ===================================================================

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