import os
from django.db import models
from django.utils.translation import gettext_lazy as _  # Tùy chọn cho TextChoices

# Create your models here.
class CandidateFile(models.Model):
    GENDER_CHOICES = (
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    )
    # Khóa chính (PK) ID sẽ được tạo tự động mặc định [7, 8].
    fullname = models.CharField(
        max_length=255,
        verbose_name="Họ và Tên"
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

    # Sử dụng FileField để lưu file CV [9-11].
    cv_file = models.FileField(upload_to="cv_files/", null=True, blank=True)
    def delete(self, *args, **kwargs):
        if self.cv_file and os.path.isfile(self.cv_file.path):
            os.remove(self.cv_file.path)
        super().delete(*args, **kwargs)

    dob = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    apply_position = models.CharField(
        max_length=100,
        null = True,
        verbose_name="Vị trí ứng tuyển"
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
        verbose_name="Trạng thái đào tạo"
    )

    class OfficialStatus(models.TextChoices):
        ACCEPTED = "PASSED", _("Đạt")

    # Đào tạo (chỉ có dữ liệu “Đạt”)
    official_status = models.CharField(
        max_length=10,
        choices=TrainingStatus.choices,
        null=True,  # Cho phép NULL
        blank=True,  # Cho phép để trống trong form
        verbose_name="Trạng thái chính thức "
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

    # Mức lương (text tự điền)
    salary = models.CharField(
        max_length=100,
        verbose_name="Mức lương",
        help_text="Ví dụ: 20-30 triệu / Theo năng lực",
        null=True,
        blank=True,
    )

    # Hình thức làm việc
    class JobType(models.TextChoices):
        FULL_TIME = "Full-time", _("Toàn thời gian")
        INTERN = "Intern", _("Thực tập")
        CONTRACT = "Contract", _("Hợp đồng")

    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
        verbose_name="Hình thức làm việc",
        null=True,
        blank=True,
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

    post_skill_needed = models.TextField(null=True, verbose_name="Kỹ năng")

#Quản lý yêu cầu tuyển dụng 2 chiều HR và Quản lý phòng ban
class recruitment_request(models.Model):
        manager_name = models.CharField(max_length=255, verbose_name="Họ và tên Quản lý")
        manager_email = models.EmailField(verbose_name="Email")
        department = models.CharField(max_length=200, verbose_name="Tên phòng ban")
        request_name = models.TextField(verbose_name="Tên yêu cầu tuyển dụng")
        quantity = models.PositiveIntegerField(
        verbose_name = "Số lượng người cần tuyển dụng",
        null = True,
        blank = True,
        )

        #Trạng thái Yêu cầu chỉ dành cho HR để chỉnh sửa
        class RequestStatus(models.TextChoices):
            CONSIDERING = "CONSIDERING", _("Đang xem xét")
            ACCEPTED = "ACCEPTED", _("Chấp nhận")
            REJECTED = "REJECTED", _("Từ chối")

        request_status = models.CharField(
            max_length=20,
            choices=RequestStatus.choices,
            default=RequestStatus.CONSIDERING,
            null=True,  # Cho phép giá trị NULL trong CSDL [18]
            blank=True,
            verbose_name="Trạng thái xét duyệt"
        )

        reason = models.TextField(verbose_name="Lý do tuyển dụng")
        job_description = models.TextField(verbose_name="Mô tả công việc")
        request_skill_needed = models.TextField(null=True, verbose_name="Kỹ năng")

        date_requested = models.DateField(
        auto_now_add=True,
        verbose_name="Ngày gửi yêu cầu"
        )

        #Ngày yêu cầu nhận việc dành cho Quản lý để nhập tay
        date_job_start = models.DateField(null=True, verbose_name="Ngày yêu cầu nhận việc")

        recruitment_position = models.CharField(
        max_length=100,
        verbose_name="Vị trí tuyển dụng"
        )

        salary_min = models.PositiveIntegerField(
        verbose_name = "Mức lương tối thiểu (VNĐ)",
        null = True,
        blank = True,
        )

        salary_max = models.PositiveIntegerField(
            verbose_name="Mức lương tối đa (VNĐ)",
            null=True,
            blank=True,
        )