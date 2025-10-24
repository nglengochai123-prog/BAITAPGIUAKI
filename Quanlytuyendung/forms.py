from django import forms
from .models import CandidateFile, Skill  # Đảm bảo đã import Skill

class CandidateFileForm(forms.ModelForm):
    # Bạn có thể thêm các ràng buộc tùy chỉnh tại đây nếu cần (ví dụ: min_length cho skill)

    class Meta:
        model = CandidateFile
        # Sử dụng "__all__" để tự động bao gồm tất cả các trường từ CandidateFile
        fields = "__all__"

        # Bạn có thể tùy chỉnh widget tại đây nếu muốn giao diện đẹp hơn
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'skill': forms.CheckboxSelectMultiple(),
        }