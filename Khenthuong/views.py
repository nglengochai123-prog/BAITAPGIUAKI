from django.shortcuts import render
from django.views.generic import ListView
from .models import RewardList

class RewardListView(ListView):
    model = RewardList
    template_name = 'reward_list.html'
    context_object_name = 'danh_sach_khen_thuong'

    def get_queryset(self):
        return RewardList.objects.select_related('employee', 'reward_announce','reward_item').order_by('-rewarded_date')
