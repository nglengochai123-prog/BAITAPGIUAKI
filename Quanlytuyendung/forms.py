from django import forms
from .models import CandidateFile, RecruitmentPost, Skill, recruitment_request

class CandidateFileForm(forms.ModelForm):
    class Meta:
        model = CandidateFile
        fields = ['fullname', 'gender', 'dob', 'phone_number', 'email', 'study','apply_position', 'cv_file', 'skill']
        widgets = {
            'fullname': forms.TextInput(attrs={'placeholder': 'Nguyễn Văn A'}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '0912345678'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'study': forms.TextInput(attrs={'placeholder': 'THPT'}),
            'apply_position': forms.TextInput(attrs={'placeholder': 'Content SEO'}),
            'cv_file': forms.ClearableFileInput(attrs={'accept': '.png,.jpg,.pdf,.doc,.docx'}),
            'skill': forms.CheckboxSelectMultiple(),
        }

#HR tạo bài đăng tuyển dụng bên HR để xem
class RecruitmentPostForm(forms.ModelForm):
    class Meta:
        model = RecruitmentPost
        fields = ['title', 'salary', 'job_type', 'status', 'content']
        labels = {
            'title': 'Vị trí tuyển dụng',
            'salary': 'Mức lương',
            'job_type': 'Hình thức làm việc',
            'status': 'Trạng thái tuyển dụng',
            'content': 'Mô tả công việc',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Senior Frontend Developer',
            }),
            'salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: 20-30 triệu',
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Mô tả chi tiết về vị trí tuyển dụng...',
            }),
        }

#Thêm Skill của HR
class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        labels = {
            'name': 'Tên kỹ năng',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên kỹ năng mới...'
            })
        }

#Gửi yêu cầu tuyển dụng chỉ dành riêng cho Quản lý
class RecruitmentRequestForm(forms.ModelForm):
    class Meta:
        model = recruitment_request
        exclude = ['request_status', 'date_requested']  # Quản lý không được chỉnh trạng thái, ngày tự tạo
        labels = {
            'manager_name': 'Họ và tên Quản lý',
            'manager_email': 'Email',
            'department': 'Tên phòng ban',
            'request_name': 'Tên yêu cầu tuyển dụng',
            'quantity': 'Số lượng cần tuyển',
            'reason': 'Lý do tuyển dụng',
            'job_description': 'Mô tả công việc',
            'request_skill_needed': 'Kỹ năng yêu cầu',
            'date_job_start': 'Ngày yêu cầu nhận việc',
            'recruitment_position': 'Vị trí tuyển dụng',
            'salary_min': 'Mức lương tối thiểu (VNĐ)',
            'salary_max': 'Mức lương tối đa (VNĐ)',
        }
        widgets = {
            'manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manager_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'request_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'job_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'request_skill_needed': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'date_job_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'recruitment_position': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('salary_min')
        max_salary = cleaned_data.get('salary_max')

        # Kiểm tra nếu cả 2 giá trị đều có
        if min_salary is not None and max_salary is not None:
            if max_salary < min_salary:
                self.add_error('salary_max', 'Mức lương tối đa phải lớn hơn hoặc bằng mức lương tối thiểu.')