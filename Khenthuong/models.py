from django.db import models
from Quanlyhoso.models import NhanVien
# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=500, verbose_name='Tên Dự Án')
    led_project = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='led_projects')
    employee = models.ManyToManyField(NhanVien, through='ProjectEmployee', related_name='employee_projects')
    description = models.TextField(verbose_name='Mô tả', help_text='Nhập mô tả dự án')
    started_date = models.DateField(auto_now_add=True, verbose_name='Ngày bắt đầu')
    ended_date = models.DateField(null=True, verbose_name='Ngày kết thúc')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Dự án'
        verbose_name_plural = 'Danh sách dự án'

class ProjectEmployee(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Mã Dự Án')
    employee = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='project_assignments')
    role = models.CharField(max_length=100, default='Thành viên', verbose_name='Vai trò')
    added_date = models.DateField(auto_now_add=True, verbose_name='Ngày tham gia')

    class Meta:
        unique_together=('project','employee','role')
        ordering = ['-project','employee']

    def __str__(self):
        return f'[P{self.project}][E{self.employee}]'

class PerformanceCriteria(models.Model):
    code = models.CharField(max_length=10, primary_key=True, verbose_name='Mã Tiêu Chí')
    name = models.CharField(max_length=255, verbose_name='Tên Tiêu Chí')

    class CriteriaType(models.TextChoices):
        QUANTITATIVE = 'QUANT', 'Định Lượng (KPI)'
        QUALITATIVE = 'QUAL', 'Định Tính'
        GOAL = 'GOAL', 'Mục Tiêu'

    type = models.CharField(max_length=10, choices=CriteriaType.choices, default=CriteriaType.QUANTITATIVE, verbose_name='Loại Tiêu Chí')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Trọng Số (%)')
    description = models.TextField(verbose_name='Mô tả chi tiết', help_text='Mô tả cách thức đánh giá và tính điểm.')

    def __str__(self):
        return f"[{self.code}] {self.name}"

    class Meta:
        verbose_name = 'Tiêu Chí Đánh Giá'
        verbose_name_plural = 'Danh Mục Tiêu Chí'

class PerformanceReview(models.Model):
    employee = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='reviews_received')
    reviewer = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='reviews_given')
    review_date = models.DateField(auto_now_add=True, verbose_name='Ngày Đánh Giá')
    period = models.CharField(max_length=50, verbose_name='Kỳ Đánh Giá', help_text='Ví dụ: Q3-2024, Năm 2024')
    final_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Điểm Tổng Kết')
    criteria = models.ManyToManyField(PerformanceCriteria, through='ScoreDetail', verbose_name='Các Tiêu Chí Áp Dụng')

    def __str__(self):
        return f"Đánh giá {self.employee} - {self.period}"

    class Meta:
        verbose_name = 'Phiếu Đánh Giá Hiệu Suất'
        verbose_name_plural = 'Quản Lý Đánh Giá Hiệu Suất'
        unique_together = ('employee', 'period')

class ScoreDetail(models.Model):
    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, verbose_name='Phiếu Đánh Giá')
    criteria = models.ForeignKey(PerformanceCriteria, on_delete=models.CASCADE,verbose_name='Tiêu Chí')
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Điểm Đạt Được')
    comment = models.TextField(blank=True, verbose_name='Nhận Xét')

    def __str__(self):
        return f"{self.review.employee} - {self.criteria.code}: {self.score} điểm"

    class Meta:
        verbose_name = 'Chi Tiết Điểm Số'
        verbose_name_plural = 'Chi Tiết Điểm Số'
        unique_together = ('review', 'criteria')

class Reward(models.Model):
    code = models.CharField(max_length=5, primary_key=True, verbose_name='Mã khen thưởng')
    name = models.CharField(max_length=500, verbose_name='Tên hạng mục Khen thưởng')

    class RewardType(models.TextChoices):
        PERIODIC = 'PERIODIC', 'Định kỳ'
        PERFORMANCE = 'PERFORMANCE', 'Hiệu suất'

    type = models.CharField(max_length=15, choices=RewardType.choices, verbose_name='Nhóm hạng mục')

    def __str__(self):
        return f'[{self.code}]{self.name}'

    class Meta:
        verbose_name = 'Hạng mục khen thưởng'
        verbose_name_plural = 'Danh mục khen thưởng'

class RewardAnnounce(models.Model):
    name = models.CharField(max_length=500, verbose_name='Tên Thông báo')
    reward_code = models.ForeignKey(Reward,on_delete=models.PROTECT, verbose_name='Hạng mục khen thưởng áp dụng')
    budget = models.IntegerField(verbose_name='Ngân sách Khen thưởng')
    maximum_employee = models.IntegerField(verbose_name='Số lượng khen thưởng tối đa')
    announced_date = models.DateField(auto_now_add=True, verbose_name='Ngày thông báo khen thưởng')
    description = models.TextField(verbose_name='Nội dung thông báo khen thưởng', help_text='Mô tả nội dung thông báo khen thưởng')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Thông báo khen thưởng'
        verbose_name_plural = 'Lịch sử thông báo khen thưởng'

class RewardSuggest(models.Model):
    employee = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='reward_suggestions')
    reward_announce = models.ForeignKey(RewardAnnounce, on_delete=models.PROTECT, verbose_name='Thông báo áp dụng')
    reward_item = models.ForeignKey(Reward, on_delete=models.PROTECT, verbose_name='Hạng mục nhận thưởng')
    suggested_by = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='suggestions_made')
    description = models.TextField(verbose_name='Lí do khen thưởng', help_text='Nhập lí do khen thưởng')

    class SuggestStatus(models.TextChoices):
        PENDING = 'PENDING', 'Chờ duyệt'
        APPROVED = 'APPROVED', 'Đã duyệt'
        REJECTED = 'REJECTED', 'Từ chối'

    status = models.CharField(max_length=15, choices=SuggestStatus.choices, default=SuggestStatus.PENDING, verbose_name='Trạng thái xét duyệt')

    def __str__(self):
        return f'[Đề xuất {self.get_status_display()}] cho E[{self.employee}] ({self.reward_item})'

    class Meta:
        verbose_name = 'Đề xuất khen thưởng'
        verbose_name_plural = 'Danh sách đề xuất khen thưởng'

class RewardList(models.Model):
    employee = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='reward_lists')
    reward_announce = models.ForeignKey(RewardAnnounce, on_delete=models.PROTECT, verbose_name='Thông báo áp dụng')
    reward_item = models.ForeignKey(Reward, on_delete=models.PROTECT, verbose_name='Hạng mục nhận thưởng')
    rewarded_value = models.IntegerField(verbose_name='Giá trị Khen thưởng')
    rewarded_date = models.DateField(auto_now_add=True, verbose_name='Ngày khen thưởng')

    def __str__(self):
         return f'E[{self.employee}] - Thưởng: {self.reward_item} ({self.rewarded_date})'

    class Meta:
        verbose_name = 'Khen thưởng'
        verbose_name_plural = 'Danh sách khen thưởng'
        unique_together = ('employee', 'reward_announce')