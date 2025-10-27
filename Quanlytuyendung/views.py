from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CandidateFileForm, RecruitmentPostForm
from .models import RecruitmentPost, CandidateFile

# View hiển thị 5 bài đăng mới nhất
def recruitment_home(request):
    # 1. Truy vấn CSDL: Sắp xếp theo ngày đăng giảm dần (mới nhất lên đầu) và chỉ lấy 5 bản ghi đầu tiên.
    # Phương thức .order_by("-field") được dùng để sắp xếp giảm dần [1, 2].
    # Việc cắt (slice) QuerySet [:5] được dùng để giới hạn số lượng [3].
    latest_posts = RecruitmentPost.objects.order_by("-date_posted")[:5]

    # 2. Tạo ngữ cảnh (context) để truyền dữ liệu sang template [4, 5].
    context = {
        'latest_posts': latest_posts,
        'title': "Tuyển dụng - Bài đăng mới nhất"
    }

    # 3. Sử dụng hàm render() để tải template và trả về kết quả [4, 6, 7].
    return render(request, 'recruitment_home.html', context)

def all_job_postings(request):
    # Lấy toàn bộ bài đăng và sắp xếp theo ngày đăng giảm dần [2, 8].
    all_posts = RecruitmentPost.objects.all().order_by("-date_posted")

    context = {
        'all_posts': all_posts,
        'title': "Toàn bộ Bài đăng Tuyển dụng"
    }

    # Render template chi tiết
    return render(request, 'all_job_postings.html', context)

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

def create_recruitment_post(request):
    # Kiểm tra phương thức gửi dữ liệu [8, 11]
    if request.method == "POST":
        # Khởi tạo form với dữ liệu POST nếu phương thức là POST [12]
        form = RecruitmentPostForm(request.POST)

        # Kiểm tra tính hợp lệ của dữ liệu form [13, 14]
        if form.is_valid():
            # Lưu bản ghi vào CSDL.
            # ModelForm tự động tạo bản ghi mới (nếu không truyền instance) [3, 15].
            new_post = form.save()

            # Đăng ký thông báo thành công và chuyển hướng (redirect)
            messages.success(request, f"Bài đăng '{new_post.content[:30]}...' đã được tạo thành công.")
            return redirect('recruitment_home')  # Thay thế bằng tên URL mong muốn sau khi tạo thành công

    else:
        # Nếu là GET, khởi tạo form rỗng [8, 16]
        form = RecruitmentPostForm()

    # Chuẩn bị context để render form
    context = {
        'form': form,
        'title': "Tạo Bài Đăng Tuyển Dụng Mới"
    }

    # Render template
    return render(request, 'recruitment_form.html', context)