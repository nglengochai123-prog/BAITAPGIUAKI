from django.db import models
from django.utils.translation import gettext_lazy as _  # Tùy chọn cho TextChoices

# Create your models here.
class CandidateFile(models.Model):
    # Khóa chính (PK) ID sẽ được tạo tự động mặc định [7, 8].
    fullname = models.CharField(
        max_length=255,
        verbose_name="Họ và Tên"
    )
    dob = models.DateField(
        verbose_name="Ngày sinh"
    )
    phonenumber = models.CharField(
        max_length=15,
        verbose_name="Số điện thoại"
    )

    # Sử dụng EmailField để đảm bảo email phải hợp lệ (PyCharm/Django sẽ kiểm tra) [5, 10, 11, 14].
    email = models.EmailField(
        max_length=255,
        verbose_name="Địa chỉ Email"
    )

    study = models.CharField(
        max_length=255,
        verbose_name="Trình độ học vấn"
    )

    # Sử dụng URLField để lưu liên kết CV [9-11].
    linkCV = models.URLField(
        verbose_name="Liên kết CV"
    )

    # Mối quan hệ Nhiều-Nhiều với Skill. Yêu cầu "tối thiểu 1 cái" cần được kiểm tra ở lớp Form (ModelForm) [3, 4].
    skill = models.ManyToManyField(
        'Skill',
        verbose_name="Kỹ năng"
    )

    # Trạng thái xét duyệt (có thể bắt đầu bằng 'Ứng tuyển')
    class ReviewStatus(models.TextChoices):
        APPLIED = "APPLIED", _("Ứng tuyển")
        SCREENING = "SCREENING", _("Sàng lọc")
        PASSED = "PASSED", _("Đạt")
        FAILED = "FAILED", _("Không đạt")

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.APPLIED,
        null=True,  # Cho phép giá trị NULL trong CSDL [18]
        blank=True,
        verbose_name="Trạng thái xét duyệt"
    )
    # Trạng thái sau phỏng vấn (Có thể NULL)
    class InterviewResult(models.TextChoices):
        PASSED = "PASSED", _("Đạt")
        FAILED = "FAILED", _("Không đạt")

    interview_result = models.CharField(
        max_length=10,
        choices=InterviewResult.choices,
        null=True, # Cho phép NULL
        blank=True, # Cho phép để trống trong form
        verbose_name="Trạng thái sau phỏng vấn"
    )

    # Trạng thái gửi offer (Có thể NULL)
    class OfferStatus(models.TextChoices):
        ACCEPTED = "ACCEPTED", _("Ứng viên đồng ý")
        REJECTED = "REJECTED", _("Ứng viên từ chối")
        EXPIRED = "EXPIRED", _("Quá hạn không phản hồi")

    offer_status = models.CharField(
        max_length=30,
        choices=OfferStatus.choices,
        null=True,
        blank=True,
        verbose_name="Trạng thái gửi offer"
    )

    class TrainingStatus(models.TextChoices):
        ACCEPTED = "PASSED", _("Đạt")

    # Đào tạo (chỉ có dữ liệu “Đạt”)
    training_status = models.CharField(
        max_length=10,
        choices=TrainingStatus.choices,
        null=True,  # Cho phép NULL
        blank=True,  # Cho phép để trống trong form
        verbose_name="Trạng thái sau phỏng vấn"
    )

    class OfficialStatus(models.TextChoices):
        ACCEPTED = "PASSED", _("Đạt")

    # Đào tạo (chỉ có dữ liệu “Đạt”)
    official_status = models.CharField(
        max_length=10,
        choices=TrainingStatus.choices,
        null=True,  # Cho phép NULL
        blank=True,  # Cho phép để trống trong form
        verbose_name="Trạng thái sau phỏng vấn"
    )

class Skill(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Tên kỹ năng"
    )
    # Phương thức __str__ giúp hiển thị tên kỹ năng trong giao diện quản trị [5, 6].
    def __str__(self):
        return self.name

class RecruitmentPost(models.Model):
    # Khóa chính (PK) ID sẽ được tạo tự động nếu không khai báo mã bài đăng (PK) tường minh [7, 8].

    # Sử dụng TextField cho thông tin chi tiết bài đăng [10, 11, 18].
    title = models.TextField(verbose_name="Tiêu đề bài đăng")
    content = models.TextField(
        verbose_name="Thông tin bài đăng"
    )

    # Ngày đăng
    date_posted = models.DateField(
        auto_now_add=True,
        verbose_name="Ngày đăng"
    )

    # Trạng thái (đã tuyển đủ/đang tuyển)
    class PostStatus(models.TextChoices):
        CLOSED = "CLOSED", _("Đã tuyển đủ")
        OPEN = "OPEN", _("Đang tuyển")

    status = models.CharField(
        max_length=10,
        choices=PostStatus.choices,
        default=PostStatus.OPEN,
        verbose_name="Trạng thái tuyển dụng"
    )