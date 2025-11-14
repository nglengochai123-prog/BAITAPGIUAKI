from django import forms
from .models import CandidateFile, Skill, RecruitmentPost # Đảm bảo đã import Skill

from django import forms
from .models import CandidateFile

class CandidateFileForm(forms.ModelForm):
    class Meta:
        model = CandidateFile
        fields = ['fullname', 'dob', 'phone_number', 'email', 'study', 'linkCV', 'skill']
        widgets = {
            'fullname': forms.TextInput(attrs={'placeholder': 'Nguyễn Văn A'}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '0912345678'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'study': forms.TextInput(attrs={'placeholder': 'THPT'}),
            'linkCV': forms.URLInput(attrs={'placeholder': 'https://drive.google.com/...'}),
            'skill': forms.CheckboxSelectMultiple(),
        }
class RecruitmentPostForm(forms.ModelForm):
    # Lớp Meta định nghĩa Model và các trường cần sử dụng [5, 6]
    class Meta:
        model = RecruitmentPost
        # Chọn các trường muốn hiển thị trong form.
        # Lưu ý: Bỏ qua các trường PK (ID) và trường auto_now_add [7].
        fields = ['content', 'status']

        # Bạn có thể tùy chỉnh widget để cải thiện giao diện (Không bắt buộc)
        widgets = {
            # Sử dụng Textarea cho trường content nếu cần thêm chiều cao
            'content': forms.Textarea(attrs={'cols': 80, 'rows': 10, 'placeholder': 'Nhập nội dung chi tiết bài đăng...'}),
        }