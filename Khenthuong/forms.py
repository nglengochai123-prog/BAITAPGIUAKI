from django import forms
from .models import Project, ProjectEmployee, RewardSuggest, PerformanceCriteria

class ProjectCreateForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'description', 'ended_date']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control border rounded-lg p-2 w-full', 'placeholder': 'Nhập tên dự án'}),
            'ended_date': forms.DateInput(attrs={'class': 'form-control border rounded-lg p-2 w-full', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control border rounded-lg p-2 w-full', 'rows': 4,
                                                 'placeholder': 'Mô tả chi tiết mục tiêu và yêu cầu dự án'}),
        }

        labels = {
            'name': 'Tên Dự Án',
            'ended_date': 'Ngày Kết Thúc Dự Kiến',
            'description': 'Mô Tả Dự Án',
        }

ProjectEmployeeFormSet = forms.inlineformset_factory(
    Project,
    ProjectEmployee,
    fields=['employee', 'role'],
    extra=1,
    can_delete=True,
    widgets={
        'employee': forms.Select(attrs={'class': 'form-control border rounded-lg p-2'}),
        'role': forms.Select(attrs={'class': 'form-control border rounded-lg p-2'}),
    }
)

class CriteriaCreateForm(forms.ModelForm):

    class Meta:
        model = PerformanceCriteria
        fields = ['name', 'type', 'weight', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control border rounded-lg p-2 w-full', 'placeholder': 'Nhập tên tiêu chí'}),
            'type': forms.Select(attrs={'class': 'form-control border rounded-lg p-2 w-full'}),
            'weight': forms.TextInput(
                attrs={'class': 'form-control border rounded-lg p-2 w-full', 'placeholder': 'Nhập trong số (%)'}),
            'description': forms.Textarea(attrs={'class': 'form-control border rounded-lg p-2 w-full', 'rows': 4,
                                                 'placeholder': 'Mô tả chi tiết tiêu chí'}),
        }

        labels = {
            'name': 'Tên Tiêu chí',
            'type': 'Loại Tiêu Chí',
            'weight': 'Trọng Số',
            'description': 'Mô Tả Tiêu Chí',
        }


class RewardSuggestForm(forms.ModelForm):

    class Meta:
        model = RewardSuggest
        fields = ['employee', 'reward_item', 'reward_announce', 'description']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control border rounded-lg p-2 w-full'}),
            'reward_item': forms.Select(attrs={'class': 'form-control border rounded-lg p-2 w-full'}),
            'reward_announce': forms.Select(attrs={'class': 'form-control border rounded-lg p-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'form-control border rounded-lg p-2 w-full', 'rows': 4,
                                                 'placeholder': 'Mô tả chi tiết thành tích và lý do đề xuất.'}),
        }
        labels = {
            'employee': 'Nhân viên được đề xuất',
            'reward_item': 'Hạng mục đề xuất',
            'reward_announce': 'Thông báo khen thưởng áp dụng',
            'description': 'Lý do đề xuất',
        }
