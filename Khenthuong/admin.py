from django.contrib import admin
from .models import Project, RewardList, RewardSuggest, ProjectEmployee, PerformanceCriteria, PerformanceReview, ScoreDetail, Reward, RewardAnnounce


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'led_project','description','started_date', 'ended_date')

class RewardListAdmin(admin.ModelAdmin):
    list_display = ('reward_item','reward_announce','rewarded_value','rewarded_date')

class ProjectEmployeeAdmin(admin.ModelAdmin):
    list_display = ('role', 'added_date')

class PerformanceCriteriaAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'weight', 'description')

class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('review_date', 'period', 'final_score')

class ScoreDetailAdmin(admin.ModelAdmin):
    list_display = ('score', 'comment')

class RewardAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type')

class RewardAnnounceAdmin(admin.ModelAdmin):
    list_display = ('name', 'budget', 'maximum_employee', 'announced_date', 'description')

class RewardSuggestAdmin(admin.ModelAdmin):
    list_display = ('description', 'status')

admin.site.register(RewardList, RewardListAdmin)
admin.site.register(ProjectEmployee, ProjectEmployeeAdmin)
admin.site.register(PerformanceCriteria, PerformanceCriteriaAdmin)
admin.site.register(PerformanceReview, PerformanceReviewAdmin)
admin.site.register(ScoreDetail, ScoreDetailAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(RewardAnnounce, RewardAnnounceAdmin)
admin.site.register(RewardSuggest, RewardSuggestAdmin)
admin.site.register(Project, ProjectAdmin)
