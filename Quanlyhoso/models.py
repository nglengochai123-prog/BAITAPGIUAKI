from django.db import models
from django.contrib.auth.models import User
class PhongBan(models.Model):
    ten_phong_ban = models.CharField(max_length=200, unique=True, verbose_name="Tên phòng ban")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Phòng Ban"
        verbose_name_plural = "Các Phòng Ban"

    def __str__(self):
        return self.ten_phong_ban
class ChucVu(models.Model):
    ten_chuc_vu = models.CharField(max_length=200, unique=True, verbose_name="Tên chức vụ")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Chức Vụ"
        verbose_name_plural = "Các Chức Vụ"

    def __str__(self):
        return self.ten_chuc_vu
class NhanVien(models.Model):
    GIOI_TINH_CHOICES = (
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    )

    TRANG_THAI_CHOICES = (
        ('Đang làm việc', 'Đang làm việc'),
        ('Đã nghỉ việc', 'Đã nghỉ việc'),
        ('Thử việc', 'Thử việc'),
    )
    fullname = models.CharField(max_length=255,verbose_name="Họ và Tên", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Tài khoản")
    ma_nhan_vien = models.CharField(max_length=20, unique=True, verbose_name="Mã nhân viên")
    phong_ban = models.ForeignKey(PhongBan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phòng ban")
    chuc_vu = models.ForeignKey(ChucVu, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Chức vụ")
    nguoi_quan_ly = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người quản lý trực tiếp")
    ngay_bat_dau_lam = models.DateField(verbose_name="Ngày bắt đầu làm việc")
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='Thử việc',
                                  verbose_name="Trạng thái")
    # Chúng ta dùng DecimalField để có thể quản lý 0.5 ngày (nửa ngày)
    so_ngay_phep_nam_con_lai = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=12.0,
        verbose_name="Số ngày phép năm còn lại"
    )
    email = models.EmailField(default='temp@example.com',max_length=255,verbose_name="Địa chỉ Email")
    anh_dai_dien = models.ImageField(upload_to='anh_dai_dien/', null=True, blank=True, verbose_name="Ảnh đại diện")
    ngay_sinh = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gioi_tinh = models.CharField(max_length=10, choices=GIOI_TINH_CHOICES, verbose_name="Giới tính")
    so_dien_thoai = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    dia_chi = models.TextField(blank=True, verbose_name="Địa chỉ")
    so_cmnd_cccd = models.CharField(max_length=20, blank=True, verbose_name="Số CMND/CCCD")
    ngay_cap = models.DateField(null=True, blank=True, verbose_name="Ngày cấp")
    noi_cap = models.CharField(max_length=200, blank=True, verbose_name="Nơi cấp")
    ma_so_thue = models.CharField(max_length=20, blank=True, verbose_name="Mã số thuế")
    so_so_bhxh = models.CharField(max_length=20, blank=True, verbose_name="Số sổ BHXH")
    class Meta:
        verbose_name = "Nhân Viên"
        verbose_name_plural = "Các Nhân Viên"

    def __str__(self):
        return f"{self.ma_nhan_vien} - {self.fullname}"
class HopDong(models.Model):
    LOAI_HOP_DONG_CHOICES = (
        ('Thử việc', 'Thử việc'),
        ('Xác định thời hạn 1 năm', 'Xác định thời hạn 1 năm'),
        ('Xác định thời hạn 3 năm', 'Xác định thời hạn 3 năm'),
        ('Không xác định thời hạn', 'Không xác định thời hạn'),
        ('Thời vụ', 'Thời vụ'),
    )

    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='hop_dong', verbose_name="Nhân viên")
    so_hop_dong = models.CharField(max_length=100, unique=True, verbose_name="Số hợp đồng")
    loai_hop_dong = models.CharField(max_length=100, choices=LOAI_HOP_DONG_CHOICES, verbose_name="Loại hợp đồng")

    ngay_ky = models.DateField(verbose_name="Ngày ký")
    ngay_bat_dau = models.DateField(verbose_name="Ngày hiệu lực")
    ngay_ket_thuc = models.DateField(null=True, blank=True, verbose_name="Ngày hết hạn (nếu có)")

    luong_co_ban = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Lương cơ bản")

    file_scan = models.FileField(upload_to='hop_dong/', null=True, blank=True, verbose_name="File scan hợp đồng")

    class Meta:
        verbose_name = "Hợp Đồng"
        verbose_name_plural = "Các Hợp Đồng"
        ordering = ['-ngay_bat_dau']  # Sắp xếp hợp đồng mới nhất lên đầu

    def __str__(self):
        return f"{self.so_hop_dong} - {self.nhan_vien.user.username}"
class DonNghiPhep(models.Model):
    LOAI_PHEP_CHOICES = (
        ('Phép năm', 'Phép năm'),
        ('Nghỉ ốm', 'Nghỉ ốm'),
        ('Nghỉ không lương', 'Nghỉ không lương'),
        ('Khác', 'Khác'),
    )

    TRANG_THAI_DON_CHOICES = (
        ('Chờ duyệt', 'Chờ duyệt'),
        ('Đã duyệt', 'Đã duyệt'),
        ('Bị từ chối', 'Bị từ chối'),
    )

    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='don_nghi_phep',
                                  verbose_name="Nhân viên")
    loai_nghi_phep = models.CharField(max_length=50, choices=LOAI_PHEP_CHOICES, verbose_name="Loại nghỉ phép")

    ngay_bat_dau = models.DateField(verbose_name="Ngày bắt đầu nghỉ")
    ngay_ket_thuc = models.DateField(verbose_name="Ngày kết thúc nghỉ")
    so_ngay_nghi = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Tổng số ngày nghỉ")

    ly_do = models.TextField(verbose_name="Lý do")
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_DON_CHOICES, default='Chờ duyệt',
                                  verbose_name="Trạng thái")

    ngay_gui_don = models.DateTimeField(auto_now_add=True, verbose_name="Ngày gửi đơn")
    nguoi_xu_ly = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='nguoi_duyet_don', verbose_name="Người xử lý (Quản lý)")
    ghi_chu_quan_ly = models.TextField(blank=True, verbose_name="Ghi chú của quản lý")

    class Meta:
        verbose_name = "Đơn Nghỉ Phép"
        verbose_name_plural = "Các Đơn Nghỉ Phép"
        ordering = ['-ngay_gui_don']

    def __str__(self):
        return f"Đơn của {self.nhan_vien.user.username} - {self.ngay_bat_dau}"
class ChamCong(models.Model):
    TRANG_THAI_CHAM_CONG_CHOICES = (
        ('Đúng giờ', 'Đúng giờ'),
        ('Đi trễ', 'Đi trễ'),
        ('Về sớm', 'Về sớm'),
        ('Vắng mặt', 'Vắng mặt'),
        ('Nghỉ phép', 'Nghỉ phép'),
    )

    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='cham_cong',
                                  verbose_name="Nhân viên")
    ngay_cham_cong = models.DateField(verbose_name="Ngày chấm công")

    gio_vao = models.TimeField(null=True, blank=True, verbose_name="Giờ vào")
    gio_ra = models.TimeField(null=True, blank=True, verbose_name="Giờ ra")

    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHAM_CONG_CHOICES, default='Đúng giờ',
                                  verbose_name="Trạng thái")
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = "Chấm Công"
        verbose_name_plural = "Dữ Liệu Chấm Công"
        # Đảm bảo mỗi nhân viên chỉ có 1 bản ghi chấm công mỗi ngày
        unique_together = ('nhan_vien', 'ngay_cham_cong')
        ordering = ['-ngay_cham_cong', 'nhan_vien']

    def __str__(self):
        return f"{self.nhan_vien.user.username} - {self.ngay_cham_cong}"


# Create your models here.
