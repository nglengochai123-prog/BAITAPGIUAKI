from django import forms
from .models import Employee, ProfileUpdateRequest, TrainingRequest, Position, Department


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfileUpdateRequest
        # Liệt kê các trường mà nhân viên ĐƯỢC PHÉP nộp
        fields = [
            'full_name',
            'avatar',
            'dob',
            'gender',
            'phone_number',
            'address',
            'cic'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Gợi ý: Làm cho các trường không bắt buộc, vì nhân viên chỉ đổi 1 vài thứ
        for field_name in self.fields:
            self.fields[field_name].required = False

        # Thêm class bootstrap cho đẹp
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
class TrainingRequestForm(forms.ModelForm):
    class Meta:
        model = TrainingRequest
        # Chỉ lấy 2 trường nhân viên cần điền
        fields = ['course_name', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm class bootstrap và placeholder cho đẹp
        self.fields['course_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ví dụ: Khóa học Python nâng cao, Kỹ năng thuyết trình...'
        })
        self.fields['reason'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Nêu rõ lý do bạn cần khóa học này và nó sẽ giúp ích gì cho công việc...'
        })
class EmployeeForm(forms.ModelForm):
    # Định nghĩa các trường DateInput để hiện lịch
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Ngày sinh", required=False)
    started_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Ngày bắt đầu làm việc")

    class Meta:
        model = Employee
        # Liệt kê TẤT CẢ các trường HR có thể nhập/sửa
        fields = [
            'employee_id', 'full_name', 'department', 'position', 'manager',
            'started_date', 'avatar', 'dob', 'gender', 'phone_number',
            'address', 'cic', 'user'
        ]
        # (Chúng ta thêm 'user' để HR có thể liên kết hồ sơ với tài khoản đăng nhập)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm class 'form-control' của Bootstrap cho tất cả các trường
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})