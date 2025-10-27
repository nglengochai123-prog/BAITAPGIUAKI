from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Sum  # Sử dụng cho các truy vấn phức tạp và tính tổng [15-17]
from django.contrib import messages  # Cần để đăng ký thông điệp (messages) [18, 19]
from decimal import Decimal  # Đảm bảo tính toán chính xác
import datetime

# Import Model NhanVien từ ứng dụng Quanlyhoso theo yêu cầu
from Quanlyhoso.models import NhanVien

# Import các Model cục bộ
from .models import (
    PayrollPeriod, EmployeeSalary, ChamCong,
    VariableBonus, PayrollEntry, SalaryComponent
)


# --- ĐỊNH NGHĨA FORM CHỌN KỲ LƯƠNG TRONG VIEWS.PY ---

class PeriodSelectionForm(forms.Form):
    """Form để người dùng chọn Kỳ lương cần tính toán."""

    period = forms.ModelChoiceField(
        # Lọc các kỳ lương chưa chốt (is_closed=False)
        queryset=PayrollPeriod.objects.filter(is_closed=False).order_by('-start_date'),
        label="Chọn Kỳ Lương",
        help_text="Chỉ hiển thị các kỳ lương chưa chốt.",
        empty_label="--- Chọn kỳ lương ---"
    )


# --- HÀM TIỆN ÍCH: LẤY SỐ NGÀY CÔNG THỰC TẾ ---

def get_actual_working_days(employee_pk, start_date, end_date):
    """Tính tổng số ngày công thực tế trong một kỳ."""

    # Lọc theo nhân viên và khoảng thời gian (sử dụng lookups __gte và __lte) [13]
    working_days_queryset = ChamCong.objects.filter(
        nhan_vien__pk=employee_pk,
        ngay_cham_cong__gte=start_date,
        ngay_cham_cong__lte=end_date
    )

    # Loại trừ các trạng thái không tính là ngày công thực tế (Vắng mặt, Nghỉ phép) [20]
    excluded_statuses = ['Vắng mặt', 'Nghỉ phép']

    total_days = working_days_queryset.exclude(
        trang_thai__in=excluded_statuses
    ).count()

    return Decimal(total_days)


# --- HÀM TIỆN ÍCH: LOGIC TÍNH LƯƠNG CỐT LÕI ---

def calculate_employee_payroll(employee_pk, period):
    """Thực hiện tính toán lương cho một nhân viên dựa trên công thức đã cho."""
    employee = get_object_or_404(NhanVien, pk=employee_pk)

    # 1. Lấy Lương Cơ Bản (BASE)
    try:
        base_salary_entry = EmployeeSalary.objects.get(
            employee=employee,
            component__component_type='BASE',
            is_active=True
        )
        luong_co_ban_rate = base_salary_entry.amount
    except EmployeeSalary.DoesNotExist:
        raise ValueError(f"Không tìm thấy Lương Cơ Bản đang hoạt động.")

    # 2. Tính Lương Cơ Bản đã điều chỉnh theo ngày công
    so_ngay_cong_chuan = period.standard_working_days
    so_ngay_cong_thuc_te = get_actual_working_days(
        employee_pk, period.start_date, period.end_date
    )

    if so_ngay_cong_chuan == 0:
        raise ValueError("Số ngày công chuẩn trong kỳ lương là 0.")

    # Công thức Lương cơ bản điều chỉnh
    base_pay_calculated = (luong_co_ban_rate / so_ngay_cong_chuan) * so_ngay_cong_thuc_te

    # 3. Tính Tổng Phụ Cấp (cố định)
    # Sử dụng aggregation SUM [21]
    fixed_allowances_qs = EmployeeSalary.objects.filter(
        employee=employee,
        component__component_type='ALLOWANCE',
        is_active=True
    ).aggregate(total=Sum('amount'))
    tong_phu_cap = fixed_allowances_qs['total'] if fixed_allowances_qs['total'] else Decimal(0)

    # 4. Tính Tổng Thưởng (biến đổi)
    total_bonus_qs = VariableBonus.objects.filter(
        employee=employee,
        period=period
    ).aggregate(total=Sum('amount'))
    tong_thuong = total_bonus_qs['total'] if total_bonus_qs['total'] else Decimal(0)

    # 5. Tính Thực lĩnh
    thuc_linh = base_pay_calculated + tong_phu_cap + tong_thuong

    # 6. Lưu kết quả vào PayrollEntry (sử dụng update_or_create) [22]
    payroll_entry, created = PayrollEntry.objects.update_or_create(
        employee=employee,
        period=period,
        defaults={
            'luong_co_ban': luong_co_ban_rate,
            'so_ngay_cong_thuc_te': so_ngay_cong_thuc_te,
            'so_ngay_cong_chuan': so_ngay_cong_chuan,
            'tong_phu_cap': tong_phu_cap,
            'tong_thuong': tong_thuong,
            'thuc_linh': thuc_linh,
        }
    )
    return payroll_entry


# --- VIEW QUẢN LÝ TÍNH LƯƠNG TỔNG HỢP ---

def payroll_management_view(request):
    """
    View tổng hợp xử lý việc chọn kỳ lương, kích hoạt tính toán và hiển thị kết quả.
    """

    # Khởi tạo form với dữ liệu GET hoặc None [23]
    period_form = PeriodSelectionForm(request.GET or None)
    period = None
    payroll_entries = []

    # 1. Xử lý POST request (Tính toán lương)
    if request.method == 'POST':
        form = PeriodSelectionForm(request.POST)  # Khởi tạo form với dữ liệu POST [23, 24]

        if form.is_valid():  # Kiểm tra tính hợp lệ của dữ liệu form [25, 26]
            period = form.cleaned_data['period']
            success_count = 0
            error_count = 0

            employees = NhanVien.objects.all()

            for employee in employees:
                try:
                    calculate_employee_payroll(employee.pk, period)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    messages.error(request,
                                   f"Lỗi tính lương cho {employee.ho_ten}: {str(e)}")  # Đăng ký thông điệp lỗi [22, 27]

            messages.success(request,
                             f"Đã hoàn thành tính lương cho kỳ {period.name}: Thành công {success_count}, Lỗi {error_count}.")

            # Chuyển hướng sau POST (Pattern Post/Redirect/Get) [27, 28]
            return redirect('payroll_management_url_name')

        else:
            # Nếu form không hợp lệ
            messages.error(request, "Dữ liệu form không hợp lệ. Vui lòng kiểm tra lại.")
            period_form = form

    # --- XỬ LÝ KHI HIỂN THỊ TRANG (GET REQUEST HOẶC SAU KHI REDIRECT) ---

    # 1. Xác định kỳ lương cần hiển thị
    if period_form.is_valid():
        period = period_form.cleaned_data['period']
    elif period is None:
        # Lấy kỳ lương gần nhất làm mặc định
        try:
            latest_period = PayrollPeriod.objects.latest('end_date')  # Sử dụng latest lookup
            period = latest_period
            period_form = PeriodSelectionForm(initial={'period': period})  # Đặt giá trị khởi tạo [29]
        except PayrollPeriod.DoesNotExist:
            period = None

    # 2. Truy xuất kết quả bảng lương để hiển thị
    if period:
        # Truy xuất tất cả bảng lương đã tính trong kỳ này
        payroll_entries = PayrollEntry.objects.filter(period=period).order_by('employee__ho_ten')

    # 3. Chuẩn bị Context
    context = {
        'period_form': period_form,
        'payroll_entries': payroll_entries,
        'period': period,
    }

    # Trả về template duy nhất (theo tên file đơn giản đã thống nhất) [14, 30]
    return render(request, 'payroll_management.html', context)