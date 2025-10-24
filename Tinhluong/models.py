from django.db import models
from django.contrib import auth
from datetime import date


class Employee(models.Model):
    # Khóa chính id (AutoField) sẽ được Django tự động tạo nếu không khai báo
    employee_code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Mã định danh duy nhất của nhân viên."
    )
    first_names = models.CharField(
        max_length=50,
        help_text="Tên của nhân viên."
    )
    last_names = models.CharField(
        max_length=50,
        help_text="Họ của nhân viên."
    )
    salary_level = models.IntegerField(
        null=True,
        blank=True,  # Cho phép trống trong form (Chương 4)
        help_text="Bậc lương để xác định mức lương cơ bản."
    )

    def __str__(self):
        # Trả về chuỗi đại diện đối tượng (tương tự Contributor [10])
        return f"{self.last_names} {self.first_names} ({self.employee_code})"

class SalaryComponent(models.Model):
    name = models.CharField(
        max_length=50,
        help_text="Tên thành phần lương (ví dụ: Lương Cơ Bản, Phụ Cấp Ăn Trưa)."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Số tiền cố định của thành phần này."
    )
    is_deduction = models.BooleanField(
        default=False,
        help_text="Đánh dấu nếu đây là khoản khấu trừ (ví dụ: Bảo hiểm xã hội)."
    )

    def __str__(self):
        return self.name


class Timesheet(models.Model):
    class StatusChoices(models.TextChoices):  # Tương tự ContributionRole [11, 12]
        PENDING = "PENDING", "Chờ Duyệt"
        APPROVED = "APPROVED", "Đã Duyệt"
        REJECTED = "REJECTED", "Từ Chối"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,  # Không cho xóa nhân viên nếu còn dữ liệu chấm công [13-15]
        help_text="Nhân viên có bảng chấm công này."
    )
    month_year = models.DateField(
        verbose_name="Tháng tính lương",  # Tên mô tả thân thiện [16]
        help_text="Ngày đầu tiên của tháng tính lương."
    )
    working_days = models.FloatField(
        help_text="Số ngày công thực tế."
    )
    overtime_hours = models.IntegerField(
        default=0,
        help_text="Số giờ tăng ca (nếu có)."
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,  # Sử dụng danh sách lựa chọn
        default=StatusChoices.PENDING,
        help_text="Trạng thái của bảng chấm công."
    )

    class Meta:
        # Đảm bảo mỗi nhân viên chỉ có một bảng chấm công cho mỗi tháng
        unique_together = ('employee', 'month_year')

    def __str__(self):
        return f"Timesheet for {self.employee.last_names} - {self.month_year.strftime('%Y-%m')}"

class CustomAdjustment(models.Model):

    class AdjustmentTypes(models.TextChoices):
        BONUS = "BONUS", "Thưởng"
        DEDUCTION = "DEDUCTION", "Khấu Trừ/Phạt"
        ALLOWANCE = "ALLOWANCE", "Phụ Cấp Khác"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE, # Xóa nhân viên thì xóa luôn các điều chỉnh liên quan [14, 17-19]
        help_text="Nhân viên áp dụng khoản điều chỉnh."
    )
    adjustment_type = models.CharField(
        max_length=20,
        choices=AdjustmentTypes.choices,
        help_text="Loại điều chỉnh (Thưởng, Phạt, Phụ cấp)."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Số tiền điều chỉnh."
    )
    notes = models.TextField(
        blank=True, # Cho phép trống trong form nhập liệu [20]
        help_text="Ghi chú chi tiết về khoản điều chỉnh."
    )
    # Khóa ngoại liên kết đến PayrollRecord (Bảng lương)
    payroll_record = models.ForeignKey(
        'PayrollRecord',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Bảng lương mà điều chỉnh này được áp dụng."
    )

    def __str__(self):
        return f"{self.adjustment_type} for {self.employee.last_names}: {self.amount}"

class PayrollRecord(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        help_text="Nhân viên nhận bảng lương."
    )
    period_start_date = models.DateField(
        help_text="Ngày bắt đầu kỳ tính lương."
    )
    period_end_date = models.DateField(
        help_text="Ngày kết thúc kỳ tính lương."
    )
    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Tổng lương trước thuế."
    )
    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Tổng các khoản khấu trừ (thuế, bảo hiểm...)."
    )
    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Lương thực nhận (Net Salary)."
    )
    processed_by = models.ForeignKey(
        auth.get_user_model(), # Liên kết đến User model của Django [6, 18]
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Người dùng (admin) đã xử lý bảng lương."
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Trạng thái đã thanh toán."
    )

    def __str__(self):
        return f"Payroll for {self.employee.last_names} ({self.period_end_date})"
