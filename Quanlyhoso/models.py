from django.db import models
from django.contrib.auth.models import User
class Department(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Tên phòng ban")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Phòng Ban"
        verbose_name_plural = "Các Phòng Ban"

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Tên chức vụ")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Chức Vụ"
        verbose_name_plural = "Các Chức Vụ"

    def __str__(self):
        return self.name

class Employee(models.Model):
    GENDER_CHOICES = (
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    )

    employee_id = models.CharField(primary_key=True, max_length=20, unique=True, verbose_name="Mã nhân viên")
    full_name = models.CharField(max_length=50, verbose_name='Họ và tên nhân viên')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phòng ban")
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Chức vụ")
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người quản lý trực tiếp")
    started_date = models.DateField(verbose_name="Ngày bắt đầu làm việc")
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True, verbose_name="Ảnh đại diện")
    dob = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Giới tính")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    cic = models.CharField(max_length=20, blank=True, verbose_name="Số CMND/CCCD")

    class Meta:
        verbose_name = "Nhân Viên"
        verbose_name_plural = "Các Nhân Viên"

    def __str__(self):
        return f"{self.employee_id} - {self.employee_id.get_full_name()}"

class Contract(models.Model):
    CONTRACT_TYPE_CHOICES = (
        ('Thử việc', 'Thử việc'),
        ('Xác định thời hạn 1 năm', 'Xác định thời hạn 1 năm'),
        ('Xác định thời hạn 3 năm', 'Xác định thời hạn 3 năm'),
        ('Không xác định thời hạn', 'Không xác định thời hạn'),
        ('Thời vụ', 'Thời vụ'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='hop_dong', verbose_name="Nhân viên")
    contract_number= models.CharField(max_length=100, unique=True, verbose_name="Số hợp đồng")
    contract_type = models.CharField(max_length=100, choices=CONTRACT_TYPE_CHOICES, verbose_name="Loại hợp đồng")
    signed_date = models.DateField(verbose_name="Ngày ký")
    started_date = models.DateField(verbose_name="Ngày hiệu lực")
    ended_date = models.DateField(null=True, blank=True, verbose_name="Ngày hết hạn (nếu có)")
    basic_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Lương cơ bản")
    file_scan = models.FileField(upload_to='hop_dong/', null=True, blank=True, verbose_name="File scan hợp đồng")

    class Meta:
        verbose_name = "Hợp Đồng"
        verbose_name_plural = "Các Hợp Đồng"
        ordering = ['-started_date']  # Sắp xếp hợp đồng mới nhất lên đầu

    def __str__(self):
        return f"{self.contract_number} - {self.employee.full_name}"

class LeaveApplication(models.Model):
    APPLICATION_TYPE_CHOICES = (
        ('Phép năm', 'Phép năm'),
        ('Nghỉ ốm', 'Nghỉ ốm'),
        ('Nghỉ không lương', 'Nghỉ không lương'),
        ('Khác', 'Khác'),
    )

    APPLICATION_SATUS_CHOICES = (
        ('Chờ duyệt', 'Chờ duyệt'),
        ('Đã duyệt', 'Đã duyệt'),
        ('Bị từ chối', 'Bị từ chối'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='don_nghi_phep', verbose_name="Nhân viên")
    application_type = models.CharField(max_length=50, choices=APPLICATION_TYPE_CHOICES, verbose_name="Loại nghỉ phép")
    started_date = models.DateField(verbose_name="Ngày bắt đầu nghỉ")
    ended_date = models.DateField(verbose_name="Ngày kết thúc nghỉ")
    total_days_off = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Tổng số ngày nghỉ")
    reason = models.TextField(verbose_name="Lý do")
    status = models.CharField(max_length=50, choices=APPLICATION_SATUS_CHOICES, default='Chờ duyệt', verbose_name="Trạng thái")
    submitted_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày gửi đơn")
    handler= models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewer', verbose_name="Người xử lý (Quản lý)")
    note = models.TextField(blank=True, verbose_name="Ghi chú của quản lý")

    class Meta:
        verbose_name = "Đơn Nghỉ Phép"
        verbose_name_plural = "Các Đơn Nghỉ Phép"
        ordering = ['-submitted_date']

    def __str__(self):
        return f"Đơn của {self.employee.full_name} - {self.started_date}"



# Create your models here.