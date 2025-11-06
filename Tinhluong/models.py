from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from Quanlyhoso.models import Employee, Contract



# Model 1: SalaryComponent (Thành phần Lương - BASE, PHỤ CẤP, THƯỞNG)
class SalaryComponent(models.Model):
    COMPONENT_TYPES = [
        ('BASE', 'Lương Cơ Bản'),
        ('ALLOWANCE', 'Phụ Cấp'),
        ('BONUS', 'Thưởng'),
    ]
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên thành phần")
    component_type = models.CharField(max_length=10, choices=COMPONENT_TYPES,
                                      default='BASE',verbose_name="Loại thành phần")  # [5, 6]

    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"

    class Meta:
        verbose_name = "Thành phần Lương"


# Model 2: EmployeeSalary (Cấu trúc Lương Cố định của NV)
class EmployeeSalary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='salary_details',
                                 verbose_name="Nhân viên")  # [7-9]
    component = models.ForeignKey(SalaryComponent, on_delete=models.PROTECT,
                                  limit_choices_to={'component_type__in': ['BASE', 'ALLOWANCE']},
                                  verbose_name="Thành phần lương")

    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Số tiền")  # [1, 10]
    is_active = models.BooleanField(default=True, verbose_name="Đang áp dụng")

    def __str__(self):
        return f"{self.employee.name} - {self.component.name}: {self.amount}"

    class Meta:
        verbose_name = "Lương Cố định Nhân viên"
        # Ràng buộc: Mỗi nhân viên chỉ có một mức lương cơ bản đang hoạt động
        unique_together = ('employee', 'component')


    # Model 3: PayrollPeriod (Kỳ Lương)

class PayrollPeriod(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên kỳ lương")
    start_date = models.DateField(verbose_name="Ngày bắt đầu")  # [10, 11]
    end_date = models.DateField(verbose_name="Ngày kết thúc")

    # Số ngày công chuẩn trong tháng (tham số quan trọng trong công thức)
    standard_working_days = models.DecimalField(max_digits=5, decimal_places=2,
                                                verbose_name="Số ngày công chuẩn")  # [1, 10]
    is_closed = models.BooleanField(default=False, verbose_name="Đã chốt kỳ")


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kỳ Lương"
        ordering = ['-start_date']  # [12]


# Model 4: ChamCong (Chấm Công) - Sử dụng Model đã cung cấp
class Timekeeping(models.Model):
    TIMEKEEPING_STATUS_CHOICES = (
        ('Đúng giờ', 'Đúng giờ'),
        ('Đi trễ', 'Đi trễ'),
        ('Về sớm', 'Về sớm'),
        ('Vắng mặt', 'Vắng mặt'),
        ('Nghỉ phép', 'Nghỉ phép'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='cham_cong', verbose_name="Nhân viên")
    date_of_attendance = models.DateField(verbose_name="Ngày chấm công")  # [10]
    check_in = models.TimeField(null=True, blank=True, verbose_name="Giờ vào")  # [10]
    check_out = models.TimeField(null=True, blank=True, verbose_name="Giờ ra")

    status = models.CharField(max_length=50, choices=TIMEKEEPING_STATUS_CHOICES, default='Đúng giờ',
                                  verbose_name="Trạng thái")  # [1]

    class Meta:
        verbose_name = "Chấm Công"
        verbose_name_plural = "Dữ Liệu Chấm Công"
        unique_together = ('employee', 'date_of_attendance')
        ordering = ['-date_of_attendance', 'employee']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date_of_attendance}"


# Model 5: VariableBonus (Thưởng Biến đổi)
class VariableBonus(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Nhân viên")
    period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT, verbose_name="Kỳ lương")

    # Model này chỉ dành cho Thưởng, có thể tham chiếu đến SalaryComponent loại BONUS
    component = models.ForeignKey(SalaryComponent, on_delete=models.PROTECT,
                                  limit_choices_to={'component_type': 'BONUS'}, verbose_name="Loại thưởng")

    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Số tiền thưởng")

    def __str__(self):
        return f"{self.employee.full_name} - {self.component.name} ({self.period.name})"

    class Meta:
        verbose_name = "Thưởng Biến đổi"


# Model 6: PayrollEntry (Lưu trữ Bảng Lương/ Thực lĩnh)
class PayrollEntry(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Nhân viên")
    period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT, verbose_name="Kỳ lương")

    # Dữ liệu đầu vào để dễ dàng kiểm tra công thức sau này
    basic_salary = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Lương cơ bản (Rate)")
    actual_worked_days = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ngày công thực tế")
    standard_worked_days = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ngày công chuẩn")
    total_allowance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Tổng Phụ cấp")
    total_reward = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Tổng Thưởng")

    # Kết quả tính toán
    received = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Thực lĩnh")
    calculated_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tính")  # [10, 13, 14]

    def __str__(self):
        return f"Bảng Lương {self.employee.full_name} - {self.period.name}"

    class Meta:
        verbose_name = "Bảng Lương Đã Tính"
        unique_together = ('employee', 'period')
