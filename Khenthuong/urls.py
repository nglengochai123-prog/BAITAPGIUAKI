from django.urls import path
from .views import RewardListView

urlpatterns = [
    path('khenthuong/danhsachkhenthuong/', RewardListView.as_view(), name='reward_list'),
]