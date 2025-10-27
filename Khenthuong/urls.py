from django.urls import path
from .views import RewardListView

urlpatterns = [
    path('danh-sach-khen-thuong/', RewardListView.as_view(), name='reward_list'),
]