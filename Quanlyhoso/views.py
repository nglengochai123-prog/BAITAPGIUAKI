from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Employee, ProfileUpdateRequest, TrainingRequest
from .forms import ProfileUpdateForm, TrainingRequestForm, EmployeeForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

def is_employee(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return False
    is_manager_or_hr = user.groups.filter(name__in=['HR', 'Quản lý phòng ban']).exists()
    return not is_manager_or_hr


def is_manager_or_hr(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True  # Superuser có mọi quyền
    return user.groups.filter(name__in=['HR', 'Quản lý phòng ban']).exists()


# ===================================================================
# --- CÁC VIEW CỦA NHÂN VIÊN ---
# (Đã thêm 'base_layout' vào context)
# ===================================================================

@login_required
@user_passes_test(is_employee, login_url='/login/')
def my_profile(request):
    try:
        employee = get_object_or_404(Employee, user=request.user)
    except Employee.DoesNotExist:
        return render(request, 'loi_khong_co_ho_so.html')
    context = {
        'employee': employee,
        'base_layout': 'baseemployee.html'  # <-- ĐÃ THÊM
    }
    return render(request, 'profile.html', context)


@login_required
@user_passes_test(is_employee, login_url='/login/')
def request_profile_update(request):
    employee = get_object_or_404(Employee, user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update_request = form.save(commit=False)
            update_request.employee = employee
            update_request.save()
            messages.success(request, 'Đã gửi yêu cầu cập nhật hồ sơ. Vui lòng chờ HR duyệt.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=employee)
    context = {
        'form': form,
        'base_layout': 'baseemployee.html'  # <-- ĐÃ THÊM
    }
    return render(request, 'request_update_form.html', context)


@login_required
@user_passes_test(is_employee, login_url='/login/')
def request_training_view(request):
    employee = get_object_or_404(Employee, user=request.user)
    if request.method == 'POST':
        form = TrainingRequestForm(request.POST)
        if form.is_valid():
            training_request = form.save(commit=False)
            training_request.employee = employee
            training_request.save()
            messages.success(request, 'Đã gửi yêu cầu đào tạo thành công. Vui lòng chờ HR/Quản lý duyệt.')
            return redirect('welcome_employee')
    else:
        form = TrainingRequestForm()
    context = {
        'form': form,
        'base_layout': 'baseemployee.html'  # <-- ĐÃ THÊM
    }
    return render(request, 'request_training_form.html', context)


# ===================================================================
# --- CÁC VIEW CỦA HR/QUẢN LÝ ---
# (Đã thêm logic 'base_layout' động)
# ===================================================================

def get_manager_or_hr_base(user):
    """Hàm trợ giúp: Trả về base.html (cho HR) hoặc basemanager.html (cho Quản lý)"""
    if user.groups.filter(name='Quản lý phòng ban').exists():
        return 'basemanager.html'
    return 'base.html'  # Mặc định cho HR/Superuser


@user_passes_test(is_manager_or_hr, login_url='/login/')
def hr_request_list(request):
    pending_requests = ProfileUpdateRequest.objects.filter(status='Chờ duyệt')
    context = {
        'requests': pending_requests,
        'base_layout': get_manager_or_hr_base(request.user)  # <-- ĐÃ THÊM
    }
    return render(request, 'hr_request_list.html', context)


@user_passes_test(is_manager_or_hr, login_url='/login/')
def hr_request_detail(request, pk):
    update_req = get_object_or_404(ProfileUpdateRequest, pk=pk, status='Chờ duyệt')
    employee = update_req.employee
    if request.method == 'POST':
        if 'approve' in request.POST:
            if update_req.full_name: employee.full_name = update_req.full_name
            if update_req.avatar: employee.avatar = update_req.avatar
            if update_req.dob: employee.dob = update_req.dob
            if update_req.gender: employee.gender = update_req.gender
            if update_req.phone_number: employee.phone_number = update_req.phone_number
            if update_req.address: employee.address = update_req.address
            if update_req.cic: employee.cic = update_req.cic
            employee.save()
            update_req.status = 'Đã duyệt'
            update_req.handler = request.user
            update_req.handled_at = timezone.now()
            update_req.save()
            messages.success(request, f"Đã duyệt và cập nhật hồ sơ cho {employee.full_name}.")
            return redirect('hr_request_list')
        elif 'reject' in request.POST:
            update_req.status = 'Bị từ chối'
            update_req.handler = request.user
            update_req.handled_at = timezone.now()
            update_req.hr_note = request.POST.get('hr_note', '')
            update_req.save()
            messages.warning(request, f"Đã từ chối yêu cầu của {employee.full_name}.")
            return redirect('hr_request_list')

    context = {
        'update_request': update_req,
        'employee': employee,
        'base_layout': get_manager_or_hr_base(request.user)  # <-- ĐÃ THÊM
    }
    return render(request, 'hr_request_detail.html', context)


# ===================================================================
# === VIEW ĐÃ SỬA: LỌC BỎ HR KHỎI DANH SÁCH CỦA QUẢN LÝ ===
# ===================================================================
@user_passes_test(is_manager_or_hr, login_url='/login/')
def employee_list_view(request):
    """
    Hiển thị danh sách nhân viên.
    ĐÃ CẬP NHẬT: Thêm logic tìm kiếm.
    """
    user = request.user
    base_layout = get_manager_or_hr_base(user)

    # === 1. LẤY TỪ KHÓA TÌM KIẾM TỪ URL ===
    search_query = request.GET.get('q', '')  # Dùng '' làm giá trị mặc định

    # === 2. LẤY DANH SÁCH GỐC (THEO QUYỀN) ===
    if user.is_superuser or user.groups.filter(name='HR').exists():
        # HR/Superuser: Lấy TẤT CẢ làm gốc
        employee_query_set = Employee.objects.all()

    elif user.groups.filter(name='Quản lý phòng ban').exists():
        # Quản lý: Lấy nhân viên CÙNG PHÒNG BAN làm gốc (và loại trừ HR)
        try:
            manager_profile = get_object_or_404(Employee, user=user)
            if manager_profile.department:
                manager_department = manager_profile.department
                employee_query_set = Employee.objects.filter(
                    department=manager_department
                ).exclude(
                    user__groups__name='HR'
                )
            else:
                employee_query_set = Employee.objects.none()
                messages.warning(request, 'Bạn chưa được gán vào phòng ban nào để quản lý.')
        except Employee.DoesNotExist:
            employee_query_set = Employee.objects.none()
            messages.error(request, 'Tài khoản quản lý của bạn chưa được liên kết với hồ sơ nhân viên.')
    else:
        employee_query_set = Employee.objects.none()

    # === 3. ÁP DỤNG BỘ LỌC TÌM KIẾM (NẾU CÓ) ===
    if search_query:
        # Lọc trên bất kỳ danh sách nào (của HR hoặc Quản lý)
        employee_query_set = employee_query_set.filter(
            Q(full_name__icontains=search_query) |  # Tìm theo tên
            Q(employee_id__icontains=search_query) |  # Tìm theo mã NV
            Q(phone_number__icontains=search_query)  # Tìm theo SĐT
        ).distinct()  # .distinct() để tránh lặp kết quả

    # Sắp xếp kết quả cuối cùng
    all_employees = employee_query_set.order_by('employee_id')

    # === 4. TRUYỀN TỪ KHÓA TÌM KIẾM VÀO CONTEXT ===
    context = {
        'employees': all_employees,
        'base_layout': base_layout,
        'search_query': search_query  # <-- Trả lại template để giữ nội dung ô search
    }
    return render(request, 'employee_list.html', context)


# ===================================================================


# ===================================================================
# === VIEW ĐÃ SỬA: CHẶN QUẢN LÝ XEM HỒ SƠ HR ===
# ===================================================================
@user_passes_test(is_manager_or_hr, login_url='/login/')
def hr_view_employee_profile(request, pk):
    """
    View cho HR/Quản lý xem hồ sơ chi tiết của một nhân viên
    """
    viewer_user = request.user
    target_employee = get_object_or_404(Employee, employee_id=pk)

    is_viewer_hr_or_su = viewer_user.is_superuser or viewer_user.groups.filter(name='HR').exists()
    is_viewer_manager = viewer_user.groups.filter(name='Quản lý phòng ban').exists()

    if is_viewer_manager and not is_viewer_hr_or_su:
        # Nếu người xem CHỈ LÀ Quản lý

        # 1. Kiểm tra xem người BỊ XEM có phải là HR không
        target_is_hr = False
        if target_employee.user:
            target_is_hr = target_employee.user.groups.filter(name='HR').exists()

        if target_is_hr:
            # NẾU NGƯỜI BỊ XEM LÀ HR -> CHẶN
            messages.error(request, 'Bạn không có quyền xem hồ sơ của nhân sự thuộc phòng HR.')
            return redirect('employee_list')

        # 2. Kiểm tra xem người BỊ XEM có cùng phòng ban không
        try:
            manager_profile = get_object_or_404(Employee, user=viewer_user)
            if target_employee.department != manager_profile.department:
                messages.error(request, 'Bạn không có quyền xem hồ sơ của nhân viên khác phòng ban.')
                return redirect('employee_list')
        except Employee.DoesNotExist:
            messages.error(request, 'Tài khoản quản lý của bạn chưa được liên kết.')
            return redirect('welcome_manager')

    # Nếu qua được các bước lọc (Viewer là HR, hoặc Target là nhân viên thường)
    base_layout = get_manager_or_hr_base(viewer_user)

    context = {
        'employee': target_employee,
        'base_layout': base_layout
    }

    # Sửa: Trỏ về 1 template 'profile.html' duy nhất
    return render(request, 'profile.html', context)


# ===================================================================


@user_passes_test(is_manager_or_hr, login_url='/login/')
def add_employee_view(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm nhân viên mới thành công.')
            return redirect('employee_list')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'form_title': 'Thêm Nhân viên mới',
        'base_layout': get_manager_or_hr_base(request.user)  # <-- ĐÃ THÊM
    }
    return render(request, 'employee_form.html', context)


@user_passes_test(is_manager_or_hr, login_url='/login/')
def edit_employee_view(request, pk):
    employee = get_object_or_404(Employee, employee_id=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật thông tin cho {employee.full_name}.')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'form_title': f'Cập nhật: {employee.full_name}',
        'base_layout': get_manager_or_hr_base(request.user)  # <-- ĐÃ THÊM
    }
    return render(request, 'employee_form.html', context)


@user_passes_test(is_manager_or_hr, login_url='/login/')
def delete_employee_view(request, pk):
    employee = get_object_or_404(Employee, employee_id=pk)
    if request.method == 'POST':
        full_name = employee.full_name
        employee.delete()
        messages.success(request, f'Đã xóa nhân viên {full_name}.')
        return redirect('employee_list')

    context = {
        'employee': employee,
        'base_layout': get_manager_or_hr_base(request.user)  # <-- ĐÃ THÊM
    }
    # SỬA LỖI TYPO
    return render(request, 'mployee_delete_confirm.html', context)


@user_passes_test(is_manager_or_hr, login_url='/login/')
def hr_training_list(request):
    pending_requests = TrainingRequest.objects.filter(status='Chờ duyệt')
    context = {
        'requests': pending_requests,
        'base_layout': get_manager_or_hr_base(request.user)  # <-- ĐÃ THÊM
    }
    return render(request, 'hr_training_list.html', context)


@user_passes_test(is_manager_or_hr, login_url='/login/')
def hr_training_detail(request, pk):
    training_req = get_object_or_404(TrainingRequest, pk=pk, status='Chờ duyệt')
    if request.method == 'POST':
        if 'approve' in request.POST:
            training_req.status = 'Đã duyệt'
            training_req.handler = request.user
            training_req.handled_at = timezone.now()
            training_req.hr_note = request.POST.get('hr_note', '')
            training_req.save()
            messages.success(request, f"Đã duyệt yêu cầu đào tạo '{training_req.course_name}' cho nhân viên.")
            return redirect('hr_training_list')
        elif 'reject' in request.POST:
            training_req.status = 'Bị từ chối'
            training_req.handler = request.user
            training_req.handled_at = timezone.now()
            training_req.hr_note = request.POST.get('hr_note', 'Không có lý do')
            training_req.save()
            messages.warning(request, f"Đã từ chối yêu cầu đào tạo.")
            return redirect('hr_training_list')

    context = {
        'training_request': training_req,
        'base_layout': get_manager_or_hr_base(request.user)  # <-- ĐÃ THÊM
    }
    return render(request, 'hr_training_detail.html', context)