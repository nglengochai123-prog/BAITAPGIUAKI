# views.py (patched) — thay thế file cũ
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Sum
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP, getcontext

# Import Employee model từ app quản lý hồ sơ của bạn
from Quanlyhoso.models import Employee

from .models import (
    PayrollPeriod, EmployeeSalary, Timekeeping,
    VariableBonus, PayrollEntry, SalaryComponent
)

# đặt precision phù hợp cho Decimal
getcontext().prec = 28

class PeriodSelectionForm(forms.Form):
    period = forms.ModelChoiceField(
        queryset=PayrollPeriod.objects.filter(is_closed=False).order_by('-start_date'),
        label="Chọn Kỳ Lương",
        help_text="Chỉ hiển thị các kỳ lương chưa chốt.",
        empty_label="--- Chọn kỳ lương ---"
    )

def get_actual_working_days(employee_pk, start_date, end_date):
    """
    Tính tổng số ngày công thực tế cho một nhân viên trong khoảng thời gian.
    Loại trừ các trạng thái: 'Vắng mặt', 'Nghỉ phép'
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
    Quy ước fields theo models.py của bạn.
    """
    employee = get_object_or_404(Employee, pk=employee_pk)

    # lấy lương cơ bản (entry có component_type == 'BASE' và is_active=True)
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

    # tổng phụ cấp cố định
    allowances_agg = EmployeeSalary.objects.filter(
        employee=employee,
        component__component_type='ALLOWANCE',
        is_active=True
    ).aggregate(total=Sum('amount'))
    total_allowance = Decimal(allowances_agg['total'] or 0)

    # tổng thưởng biến đổi cho kỳ
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

def payroll_management_view(request):
    period_form = PeriodSelectionForm(request.POST or None)
    period = None
    payroll_entries = []

    # POST: thực hiện tính lương cho tất cả nhân viên
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
                    # dùng full_name nếu có, fallback sang name hoặc str(emp)
                    name = getattr(emp, 'full_name', getattr(emp, 'name', str(emp)))
                    messages.error(request, f"Lỗi tính lương cho {name}: {e}")

            messages.success(request, f"Hoàn tất tính lương: thành công {success}, lỗi {errors}.")
            return redirect('payroll_management_view')
        else:
            messages.error(request, "Form không hợp lệ.")
            period_form = form

    # GET hoặc sau redirect: chọn period mặc định nếu có
    if period_form.is_valid():
        period = period_form.cleaned_data.get('period')
    else:
        try:
            latest = PayrollPeriod.objects.latest('end_date')
            period = latest
            period_form = PeriodSelectionForm(initial={'period': period})
        except PayrollPeriod.DoesNotExist:
            period = None

    if period:
        payroll_entries = PayrollEntry.objects.filter(period=period).select_related('employee').order_by('employee__pk')

    context = {
        'period_form': period_form,
        'payroll_entries': payroll_entries,
        'period': period,
    }
    return render(request, 'payroll_management.html', context)
