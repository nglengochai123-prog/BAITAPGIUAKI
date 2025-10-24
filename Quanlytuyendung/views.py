from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CandidateFileForm
from .models import CandidateFile

def welcome_view(request):
    # Hàm render sẽ tìm và tải base.html lên
    return render(request, 'base.html')

def tuyendung(request):
    return render(request, 'Quanlytuyendung/tuyendung.html')

# Trang danh sách bài đăng tuyển dụng
def baidang_list(request):
    return render(request, 'Quanlytuyendung/baidang_list.html')

# Trang quản lý tuyển dụng
def quanly_tuyendung(request):
    return render(request, 'Quanlytuyendung/quanly_tuyendung.html')

def candidate_apply(request):
    if request.method == "POST":
        # Khởi tạo form với dữ liệu từ POST
        form = CandidateFileForm(request.POST)

        if form.is_valid():
            # Lưu ModelForm: form.save() tự động tạo/cập nhật bản ghi Model trong CSDL [21]
            new_candidate = form.save()

            # Đăng ký thông điệp thành công và chuyển hướng [22, 23]
            messages.success(request, f"Hồ sơ của {new_candidate.fullname} đã được gửi thành công.")

            # Chuyển hướng đến một trang thành công (ví dụ: trang chào mừng)
            # Giả sử bạn có URL name là 'welcome_view'
            return redirect('welcome_view')

    else:
        # Nếu không phải POST (lần đầu truy cập), khởi tạo form trống [16, 17]
        form = CandidateFileForm()

    context = {
        "form": form
    }

    # Render template form nhập liệu [24]
    return render(request, "candidate_form.html", context)