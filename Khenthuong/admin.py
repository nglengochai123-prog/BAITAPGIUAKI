from django.contrib import admin
from .models import Project, RewardList, RewardSuggest, ProjectEmployee, PerformanceCriteria, PerformanceReview, ScoreDetail, Reward, RewardAnnounce

admin.site.register(RewardList)
admin.site.register(ProjectEmployee)
admin.site.register(PerformanceCriteria)
admin.site.register(PerformanceReview)
admin.site.register(ScoreDetail)
admin.site.register(Reward)
admin.site.register(RewardAnnounce)
admin.site.register(RewardSuggest)
admin.site.register(Project)
