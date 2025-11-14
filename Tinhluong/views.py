# views.py (patched & documented)
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Sum, Q
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP, getcontext
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse

# Import models từ app quản lý hồ sơ (Quanlyhoso)
from Quanlyhoso.models import Employee, Department

# Import models của app Tinhluong
from .models import (
    PayrollPeriod, EmployeeSalary, Timekeeping,
    VariableBonus, PayrollEntry, SalaryComponent
)

# openpyxl để xuất Excel
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# đặt precision phù hợp cho Decimal
getcontext().prec = 28


# ------------------------------
# Form chọn kỳ (giữ như cũ, có help_text)
# ------------------------------
class PeriodSelectionForm(forms.Form):
    period = forms.ModelChoiceField(
        queryset=PayrollPeriod.objects.filter(is_closed=False).order_by('-start_date'),
        label="Chọn Kỳ Lương",
        help_text="Chỉ hiển thị các kỳ lương chưa chốt.",
        empty_label="--- Chọn kỳ lương ---"
    )


# ------------------------------
# Helpers: tính ngày công & tính lương 1 nhân viên
# ------------------------------
def get_actual_working_days(employee_pk, start_date, end_date):
    """
    Tính tổng số ngày công thực tế cho một nhân viên trong khoảng thời gian.
    Loại trừ các trạng thái: 'Vắng mặt', 'Nghỉ phép'
    Trả về Decimal (sẵn sàng cho tính toán tiền).
    """
    qs = Timekeeping.objects.filter(
        employee__pk=employee_pk,
        date_of_attendance__gte=start_date,
        date_of_attendance__lte=end_date
    )
    excluded = ['Vắng mặt', 'Nghỉ phép']
    counted = qs.exclude(status__in=excluded).count()
    return Decimal(counted)


def calculate_employee_payroll(employee_pk, period):
    """
    Tính lương cho 1 nhân viên trong 1 kỳ và lưu/update PayrollEntry.
    - Lấy Lương Cơ Bản (component_type == 'BASE') đang active
    - Tính prorated base pay theo ngày công thực tế
    - Cộng phụ cấp (component_type == 'ALLOWANCE')
    - Cộng thưởng biến đổi (VariableBonus)
    - Lưu vào PayrollEntry (update_or_create)
    Trả về instance PayrollEntry.
    """
    employee = get_object_or_404(Employee, pk=employee_pk)

    # lấy lương cơ bản (giả định EmployeeSalary có component.component_type == 'BASE')
    try:
        base_entry = EmployeeSalary.objects.get(
            employee=employee,
            component__component_type='BASE',
            is_active=True
        )
        base_rate = Decimal(base_entry.amount)
    except EmployeeSalary.DoesNotExist:
        raise ValueError("Không tìm thấy Lương Cơ Bản đang áp dụng cho nhân viên này.")

    standard_days = Decimal(period.standard_working_days)
    actual_days = get_actual_working_days(employee_pk, period.start_date, period.end_date)

    if standard_days == 0:
        raise ValueError("Số ngày công chuẩn không thể bằng 0.")

    # base pay prorated
    base_pay_calculated = (base_rate / standard_days) * actual_days

    # tổng phụ cấp cố định (component_type == 'ALLOWANCE')
    allowances_agg = EmployeeSalary.objects.filter(
        employee=employee,
        component__component_type='ALLOWANCE',
        is_active=True
    ).aggregate(total=Sum('amount'))
    total_allowance = Decimal(allowances_agg['total'] or 0)

    # tổng thưởng biến đổi cho kỳ (VariableBonus model)
    bonus_agg = VariableBonus.objects.filter(
        employee=employee,
        period=period
    ).aggregate(total=Sum('amount'))
    total_bonus = Decimal(bonus_agg['total'] or 0)

    # tổng thực lĩnh
    received = base_pay_calculated + total_allowance + total_bonus

    # làm tròn 2 chữ số
    q = Decimal('0.01')
    base_rate_q = base_rate.quantize(q, rounding=ROUND_HALF_UP)
    actual_days_q = actual_days.quantize(q, rounding=ROUND_HALF_UP)
    standard_days_q = standard_days.quantize(q, rounding=ROUND_HALF_UP)
    base_pay_calc_q = base_pay_calculated.quantize(q, rounding=ROUND_HALF_UP)
    total_allowance_q = total_allowance.quantize(q, rounding=ROUND_HALF_UP)
    total_bonus_q = total_bonus.quantize(q, rounding=ROUND_HALF_UP)
    received_q = received.quantize(q, rounding=ROUND_HALF_UP)

    # ghi vào PayrollEntry (atomic)
    with transaction.atomic():
        entry, created = PayrollEntry.objects.update_or_create(
            employee=employee,
            period=period,
            defaults={
                'basic_salary': base_rate_q,
                'actual_worked_days': actual_days_q,
                'standard_worked_days': standard_days_q,
                'total_allowance': total_allowance_q,
                'total_reward': total_bonus_q,
                'received': received_q,
            }
        )
    return entry


# ------------------------------
# Main view: payroll_management_view
# - xử lý POST: thực hiện tính lương cho tất cả nhân viên (khi bạn bấm nút)
# - xử lý GET: hiển thị bảng lương cho kỳ được chọn (hoặc latest có dữ liệu)
# - hỗ trợ filter: q (tên/mã), component (thành phần), department (phòng ban)
# ------------------------------
def payroll_management_view(request):
    # Khởi tạo form chọn kỳ (dùng cho POST)
    period_form = PeriodSelectionForm(request.POST or None)

    # Mặc định: không có period
    period = None

    # -------------------------
    # POST: thực hiện tính lương cho tất cả nhân viên
    # -------------------------
    if request.method == 'POST':
        form = PeriodSelectionForm(request.POST)
        if form.is_valid():
            period = form.cleaned_data['period']
            success = 0
            errors = 0

            employees = Employee.objects.all().order_by('pk')
            for emp in employees:
                try:
                    calculate_employee_payroll(emp.pk, period)
                    success += 1
                except Exception as e:
                    errors += 1
                    name = getattr(emp, 'full_name', getattr(emp, 'name', str(emp)))
                    messages.error(request, f"Lỗi tính lương cho {name}: {e}")

            messages.success(request, f"Hoàn tất tính lương: thành công {success}, lỗi {errors}.")
            # Redirect về trang chính kèm param ?period=ID để hiển thị kết quả vừa tính
            return redirect(f"{reverse('payroll_management_view')}?period={period.id}")
        else:
            messages.error(request, "Form không hợp lệ.")
            period_form = form

    # -------------------------
    # GET: xác định period để hiển thị
    #  - nếu ?period=ID có trong querystring -> dùng period đó
    #  - ngược lại -> tìm latest period mà đã có PayrollEntry và hiển thị (tiện cho xem)
    # -------------------------
    pid = request.GET.get("period")
    if pid:
        try:
            period = PayrollPeriod.objects.get(pk=int(pid))
        except (PayrollPeriod.DoesNotExist, ValueError):
            period = None
    else:
        # Nếu không có ?period, lấy latest period có dữ liệu (nếu có)
        latest_with_data = PayrollEntry.objects.order_by('-period__start_date').first()
        if latest_with_data:
            period = latest_with_data.period

    # -------------------------
    # FILTER / SEARCH / COMPONENT / DEPARTMENT
    # -------------------------
    payroll_entries = []
    salary_components = SalaryComponent.objects.all().order_by('name')
    departments = Department.objects.all().order_by('name')

    if period:
        # GET params
        q = request.GET.get('q', '').strip()
        comp_id = request.GET.get('component', '').strip()
        dept_id = request.GET.get('department', '').strip()

        # base queryset (chỉ entries cho period)
        qs = PayrollEntry.objects.filter(period=period).select_related('employee')

        # 1) search theo tên hoặc mã NV
        if q:
            qs = qs.filter(
                Q(employee__full_name__icontains=q) |
                Q(employee__employee_id__icontains=q)
            )

        # 2) filter theo thành phần lương
        if comp_id:
            try:
                comp_id_int = int(comp_id)
                # models.EmployeeSalary khai related_name='salary_details'
                qs = qs.filter(employee__salary_details__component__pk=comp_id_int)
            except ValueError:
                pass

        # 3) filter theo phòng ban
        if dept_id:
            try:
                dept_id_int = int(dept_id)
                qs = qs.filter(employee__department__pk=dept_id_int)
            except ValueError:
                pass

        # remove duplicates and order
        payroll_entries = list(qs.distinct().order_by('-received'))

    # chuẩn bị context cho template
    context = {
        'period_form': period_form,
        'payroll_entries': payroll_entries,
        'period': period,
        'salary_components': salary_components,
        'departments': departments,
    }
    return render(request, 'payroll_management.html', context)


# ------------------------------
# Payslip detail view (giữ nguyên)
# ------------------------------
def payroll_detail_view(request, entry_id):
    entry = get_object_or_404(PayrollEntry, pk=entry_id)

    timekeeping_records = Timekeeping.objects.filter(
        employee=entry.employee,
        date_of_attendance__gte=entry.period.start_date,
        date_of_attendance__lte=entry.period.end_date
    ).order_by('date_of_attendance')

    context = {
        'entry': entry,
        'employee': entry.employee,
        'period': entry.period,
        'timekeeping_records': timekeeping_records,
    }
    return render(request, 'payslip_detail.html', context)


# ------------------------------
# Export Excel: support both path param (period_id) OR GET ?period=
# ------------------------------
def export_payroll_excel(request, period_id=None):
    # accept either path param or ?period=
    pid = period_id or request.GET.get('period')
    if not pid:
        return HttpResponseBadRequest("Missing 'period' parameter for export.")
    try:
        pid = int(pid)
    except ValueError:
        return HttpResponseBadRequest("Invalid 'period' parameter for export.")

    period = get_object_or_404(PayrollPeriod, pk=pid)

    # Build queryset and apply same filters if present in GET
    qs = PayrollEntry.objects.filter(period=period).select_related('employee')

    q = request.GET.get('q', '').strip()
    comp_id = request.GET.get('component', '').strip()
    dept_id = request.GET.get('department', '').strip()

    if q:
        qs = qs.filter(Q(employee__full_name__icontains=q) | Q(employee__employee_id__icontains=q))

    if comp_id:
        try:
            comp_id_int = int(comp_id)
            qs = qs.filter(employee__salary_details__component__pk=comp_id_int)
        except ValueError:
            pass

    if dept_id:
        try:
            dept_id_int = int(dept_id)
            qs = qs.filter(employee__department__pk=dept_id_int)
        except ValueError:
            pass

    entries = qs.distinct().order_by('-received')

    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = f"Payroll {period.name}"

    # Header
    headers = [
        "Mã NV", "Tên nhân viên",
        "Lương cơ bản", "Ngày công thực tế", "Ngày công chuẩn",
        "Phụ cấp", "Thưởng", "Thực lĩnh"
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Data rows
    for entry in entries:
        ws.append([
            getattr(entry.employee, 'employee_id', ''),
            getattr(entry.employee, 'full_name', str(entry.employee)),
            float(entry.basic_salary or 0),
            float(entry.actual_worked_days or 0),
            float(entry.standard_worked_days or 0),
            float(entry.total_allowance or 0),
            float(entry.total_reward or 0),
            float(entry.received or 0),
        ])

    # Auto width
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    # Response
    filename = f"payroll_{period.name.replace(' ', '_')}.xlsx"
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response
