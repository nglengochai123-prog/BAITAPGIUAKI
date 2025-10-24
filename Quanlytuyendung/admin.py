from django.contrib import admin
from .models import CandidateFile, Skill, Status, OfficialEmployee, RecruitmentPost

class CandidateFileAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'phonenumber', 'dob', 'study')
    search_fields = ('fullname', 'email', 'phonenumber', 'linkCV')

class StatusAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'review_status', 'interview_result', 'offer_status')
    # Thêm bộ lọc để theo dõi tiến trình
    list_filter = ('review_status', 'interview_result', 'offer_status')
    search_fields = ('candidate__fullname',)

class OfficialEmployeeAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'training_status', 'official_status')
    search_fields = ('candidate__fullname',)
    # Các trường này chỉ có giá trị cố định ("Đạt", "Thành công") nên có thể đặt là chỉ đọc
    readonly_fields = ('training_status', 'official_status')
class RecruitmentPostAdmin(admin.ModelAdmin):
    list_display = ('content', 'date_posted')

# Register your models here.
admin.site.register(CandidateFile, CandidateFileAdmin)
admin.site.register(Skill)
admin.site.register(Status, StatusAdmin)
admin.site.register(OfficialEmployee, OfficialEmployeeAdmin)
admin.site.register(RecruitmentPost)
