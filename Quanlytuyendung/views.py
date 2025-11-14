from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .forms import CandidateFileForm, RecruitmentPostForm, SkillForm, RecruitmentRequestForm
from .models import RecruitmentPost, CandidateFile, Skill, recruitment_request

#Trang tổng quan quản lý tuyển dụng của HR
def quanly_tuyendung(request):
    # Lấy 5 bài đăng mới nhất
    latest_posts = RecruitmentPost.objects.order_by('-date_posted')[:5]

    # Thống kê nhanh
    total_candidates = CandidateFile.objects.count()
    total_skills = Skill.objects.count()
    total_requests = recruitment_request.objects.count()
    total_posts = RecruitmentPost.objects.count()

    context = {
        'title': 'Bảng điều khiển tuyển dụng',
        'latest_posts': latest_posts,
        'total_candidates': total_candidates,
        'total_skills': total_skills,
        'total_requests': total_requests,
        'total_posts': total_posts,
    }
    return render(request, 'recruitment_dashboard.html', context)


# View hiển thị 5 bài đăng mới nhất của ứng viên
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
    all_posts = RecruitmentPost.objects.filter(status='OPEN').order_by('-date_posted')

    context = {
        'all_posts': all_posts,
        'title': "Toàn bộ Bài đăng Tuyển dụng"
    }

    # Render template chi tiết
    return render(request, 'all_job_postings.html', context)

#Hiện bài đăng tuyển dụng có nút chỉnh, xóa cho HR+thêm xuất hiện tạo bài đăng bên cạnh
def all_job_postings_hr(request):
    # Nếu người dùng gửi form tạo bài đăng
    if request.method == 'POST':
        form = RecruitmentPostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã đăng tin tuyển dụng thành công!")
            return redirect('all_job_postings_hr')
    else:
        form = RecruitmentPostForm()

    # Lấy danh sách tất cả bài đăng
    all_posts = RecruitmentPost.objects.all().order_by('-date_posted')

    # Render giao diện (gộp form + danh sách)
    return render(request, 'all_job_postings_hr.html', {
        'form': form,
        'all_posts': all_posts,
        'title': 'Tuyển Dụng',
    })

#Chỉnh sửa bài đăng của HR
def edit_recruitment_post(request, pk):
    post = get_object_or_404(RecruitmentPost, pk=pk)

    if request.method == 'POST':
        form = RecruitmentPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật bài đăng thành công.")
            return redirect('all_job_postings_hr')
    else:
        form = RecruitmentPostForm(instance=post)

    return render(request, 'edit_recruitment_post.html', {
        'form': form,
        'post': post,
        'title': f"Chỉnh sửa: {post.title}"
    })

#Xóa bài đăng của HR
def delete_recruitment_post(request, pk):
    post = get_object_or_404(RecruitmentPost, pk=pk)
    post.delete()
    messages.success(request, "Đã xóa bài đăng thành công.")
    return redirect('all_job_postings_hr')

#Form tuyển dụng của ứng viên
def candidate_apply(request):
    if request.method == "POST":
        # Khởi tạo form với dữ liệu từ POST
        form = CandidateFileForm(request.POST, request.FILES)

        if form.is_valid():
            # Lưu ModelForm: form.save() tự động tạo/cập nhật bản ghi Model trong CSDL [21]
            new_candidate = form.save()

            # Đăng ký thông điệp thành công và chuyển hướng [22, 23]
            messages.success(request, f"Hồ sơ của {new_candidate.fullname} đã được gửi thành công.")

            # Chuyển hướng đến một trang thành công (ví dụ: trang chào mừng)
            # Giả sử bạn có URL name là 'welcome_view'
            return redirect('candidate_apply')

    else:
        # Nếu không phải POST (lần đầu truy cập), khởi tạo form trống [16, 17]
        form = CandidateFileForm()

    context = {
        "form": form
    }

    # Render template form nhập liệu [24]
    return render(request, 'candidate_form.html', context)
'''
def create_recruitment_post(request):
    # Nếu người dùng nhấn nút "Đăng bài" (POST request)
    if request.method == "POST":
        form = RecruitmentPostForm(request.POST)

        if form.is_valid():
            # Lưu bản ghi mới vào cơ sở dữ liệu
            new_post = form.save()

            # Hiển thị thông báo thành công (sử dụng messages framework)
            messages.success(
                request,
                f"Bài đăng '{new_post.title[:40]}...' đã được tạo thành công."
            )

            # Chuyển hướng sau khi lưu thành công (ví dụ về trang danh sách bài đăng)
            return redirect('all_job_postings_hr')
    else:
        # Nếu chỉ là truy cập trang lần đầu (GET request)
        form = RecruitmentPostForm()

    # Trả dữ liệu context cho template
    context = {
        'form': form,
        'title': "Tạo Bài Đăng Tuyển Dụng Mới"
    }

    # Render giao diện form
    return render(request, 'recruitment_form.html', context)
'''

def recruitment_post_detail(request, pk):
    post = get_object_or_404(RecruitmentPost, pk=pk)
    context = {
        'post': post
    }
    return render(request, 'recruitment_post_detail.html', context)

#Quản lý trạng thái ứng viên của HR (có dùng Q để filter?)
def manage_status(request):
    candidates = CandidateFile.objects.all()

    # ====== 1: XỬ LÝ LỌC (GET request) ======
    if request.method == 'GET':
        keyword = request.GET.get("keyword", "")
        review_status = request.GET.get("review_status", "")
        interview_result = request.GET.get("interview_result", "")
        offer_status = request.GET.get("offer_status", "")
        training_status = request.GET.get("training_status", "")
        official_status = request.GET.get("official_status", "")

        # Tìm kiếm theo tên, email hoặc số điện thoại
        if keyword:
            candidates = candidates.filter(
                Q(fullname__icontains=keyword) |
                Q(email__icontains=keyword) |
                Q(phone_number__icontains=keyword)
            )

        # Lọc theo từng trạng thái nếu có chọn
        if review_status:
            candidates = candidates.filter(review_status=review_status)
        if interview_result:
            candidates = candidates.filter(interview_result=interview_result)
        if offer_status:
            candidates = candidates.filter(offer_status=offer_status)
        if training_status:
            candidates = candidates.filter(training_status=training_status)
        if official_status:
            candidates = candidates.filter(official_status=official_status)

    # ====== 2: XỬ LÝ CẬP NHẬT TRẠNG THÁI (POST request) ======
    elif request.method == 'POST':
        for candidate in candidates:
            review_status = request.POST.get(f'review_status_{candidate.id}')
            interview_result = request.POST.get(f'interview_result_{candidate.id}')
            offer_status = request.POST.get(f'offer_status_{candidate.id}')
            training_status = request.POST.get(f'training_status_{candidate.id}')
            official_status = request.POST.get(f'official_status_{candidate.id}')

            candidate.review_status = review_status
            candidate.interview_result = interview_result
            candidate.offer_status = offer_status
            candidate.training_status = training_status
            candidate.official_status = official_status
            candidate.save()

        return redirect('manage_status')

    # ====== 3: TRẢ DỮ LIỆU CHO TEMPLATE ======
    return render(request, 'manage_status.html', {
        'candidates': candidates,
    })

#Xem thông tin hồ sơ ứng viên trong trạng thái của HR
def view_candidate(request, pk):
    candidate = get_object_or_404(CandidateFile, pk=pk)
    return render(request, 'view_candidate.html', {'candidate': candidate})

#Nút xóa thông tin ứng viên từ manage-status
def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(CandidateFile, id=candidate_id)
    if request.method == 'POST':
        candidate.delete()
        messages.success(request, "Ứng viên đã được xóa thành công.")
        return redirect('manage_status')  # quay về trang danh sách
    else:
        messages.error(request, "Phương thức không hợp lệ.")
        return redirect('manage_status')

#HR chỉnh trạng thái của từng ứng viên
def edit_status(request, candidate_id):
    candidate = get_object_or_404(CandidateFile, id=candidate_id)

    if request.method == 'POST':
        candidate.review_status = request.POST.get('review_status')
        candidate.interview_result = request.POST.get('interview_result')
        candidate.offer_status = request.POST.get('offer_status')
        candidate.training_status = request.POST.get('training_status')
        candidate.official_status = request.POST.get('official_status')
        candidate.save()
        return redirect('manage_status')

    return render(request, 'edit_status.html', {'candidate': candidate})

#Thêm Skill của HR
def add_skill(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Kỹ năng mới đã được thêm thành công!")
            return redirect('add_skill')  # quay lại chính trang đó
    else:
        form = SkillForm()

    all_skills = Skill.objects.all().order_by('name')  # hiển thị danh sách kỹ năng hiện có
    return render(request, 'add_skill.html', {
        'form': form,
        'all_skills': all_skills,
        'title': 'Thêm kỹ năng mới'
    })

#Xóa Skill của HR
def delete_skill(request, skill_id):
    from django.shortcuts import get_object_or_404
    skill = get_object_or_404(Skill, id=skill_id)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, "Kỹ năng đã được xóa thành công!")
    return redirect('add_skill')

#HR chấp nhận hoặc từ chối yêu cầu tuyển dụng của quản lý
def manage_requests_hr(request):
    all_requests = recruitment_request.objects.all().order_by('-date_requested')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')  # 'accept', 'reject', 'reset'
        req = get_object_or_404(recruitment_request, id=request_id)

        if action == 'accept':
            req.request_status = recruitment_request.RequestStatus.ACCEPTED
            messages.success(request, f"Đã chấp nhận yêu cầu '{req.request_name}'.")
        elif action == 'reject':
            req.request_status = recruitment_request.RequestStatus.REJECTED
            messages.success(request, f"Đã từ chối yêu cầu '{req.request_name}'.")
        elif action == 'reset':
            req.request_status = recruitment_request.RequestStatus.CONSIDERING
            messages.success(request, f"Đã đặt lại trạng thái yêu cầu '{req.request_name}'.")
        req.save()
        return redirect('manage_requests_hr')

    return render(request, 'manage_requests_hr.html', {
        'all_requests': all_requests,
        'title': 'Quản lý Yêu Cầu Tuyển Dụng',
    })

#QUẢN LÝ
#Form gửi yêu cầu tuyển dụng của Quản lý
def all_recruitment_requests_manager(request):
    # Nếu gửi form tạo yêu cầu mới
    if request.method == 'POST':
        form = RecruitmentRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Yêu cầu đã gửi thành công!")
            return redirect('all_recruitment_requests_manager')
    else:
        form = RecruitmentRequestForm()

    # Lấy danh sách tất cả yêu cầu của quản lý
    all_requests = recruitment_request.objects.all().order_by('-date_requested')

    return render(request, 'all_recruitment_requests_manager.html', {
        'form': form,
        'all_requests': all_requests,
        'title': 'Yêu Cầu Tuyển Dụng',
    })

#Quản lý chỉnh sửa yêu cầu tuyển dụng
def edit_recruitment_request(request, request_id):
    req = get_object_or_404(recruitment_request, id=request_id)

    if request.method == 'POST':
        form = RecruitmentRequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, "Yêu cầu đã được cập nhật thành công!")
            return redirect('all_recruitment_requests_manager')
    else:
        form = RecruitmentRequestForm(instance=req)

    return render(request, 'edit_recruitment_request.html', {
        'form': form,
        'request_obj': req,
        'title': 'Chỉnh sửa yêu cầu'
    })

#Quản lý xóa yêu cầu tuyển dụng
def delete_recruitment_request(request, request_id):
    req = get_object_or_404(recruitment_request, id=request_id)
    if request.method == 'POST':
        req.delete()
        messages.success(request, "Yêu cầu đã được xóa thành công!")
        return redirect('all_recruitment_requests_manager')
    else:
        messages.error(request, "Phương thức không hợp lệ.")
        return redirect('all_recruitment_requests_manager')