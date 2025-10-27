from django.contrib import admin
from .models import CandidateFile, Skill, RecruitmentPost

class CandidateFileAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'phonenumber', 'dob', 'study', 'review_status', 'interview_result', 'offer_status', 'training_status', 'official_status')
    search_fields = ('fullname', 'email', 'phonenumber', 'linkCV', 'review_status', 'interview_result', 'offer_status')

class RecruitmentPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'date_posted')

# Register your models here.
admin.site.register(CandidateFile, CandidateFileAdmin)
admin.site.register(Skill)
admin.site.register(RecruitmentPost, RecruitmentPostAdmin)
