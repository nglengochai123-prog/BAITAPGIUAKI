from django.contrib import admin
from .models import CandidateFile, Skill, RecruitmentPost

class CandidateFileAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'so_dien_thoai')

class RecruitmentPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'date_posted')

# Register your models here.
admin.site.register(CandidateFile, CandidateFileAdmin)
admin.site.register(Skill)
admin.site.register(RecruitmentPost, RecruitmentPostAdmin)
