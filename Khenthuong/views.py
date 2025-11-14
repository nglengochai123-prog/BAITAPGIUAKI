from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, RewardList, RewardSuggest, RewardAnnounce, PerformanceCriteria
from .forms import RewardSuggestForm, ProjectCreateForm, ProjectEmployeeFormSet, CriteriaCreateForm

def project_list(request):

    project_list = Project.objects.order_by('-started_date')

    context = {
        'project_list': project_list,
        'page_title': 'Danh sách dự án'
    }

    return render(request, 'project_list.html', context)

def project_create(request):
    if request.method == 'POST':
        form = ProjectCreateForm(request.POST)

        if form.is_valid():
            new_project = form.save()

            messages.success(request, f" Dự án {new_project.name} đã được tạo thành công. Vui lòng thêm thành viên")

            return redirect('project_edit', pk=new_project.pk)

        else:
            messages.error(request, 'Có lỗi xảy ra trong quá trình tạo dự án. Vui lòng kiểm tra lại thông tin.')

    else:
        form = ProjectCreateForm()

    context = {
        'page_title': 'Tạo dự án mới',
        'form': form
    }
    return render(request, 'project_create.html', context)


def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    project_form = ProjectCreateForm(request.POST or None, instance=project)

    employee_formset = ProjectEmployeeFormSet(request.POST or None, instance=project)

    if request.method == 'POST':
        if project_form.is_valid() and employee_formset.is_valid():
            project_form.save()  # Lưu thông tin dự án (Tên, Mô tả...)
            employee_formset.save()  # Lưu/Cập nhật/Xóa các thành viên

            messages.success(request, f'Dự án {project.name} và danh sách thành viên đã được cập nhật thành công.')
            return redirect('project_list')
        else:
            messages.error(request, 'Có lỗi xảy ra trong quá trình cập nhật. Vui lòng kiểm tra lại thông tin.')

    context = {
        'page_title': f'Chỉnh Sửa Dự Án: {project.name}',
        'project': project,
        'project_form': project_form,
        'employee_formset': employee_formset,
    }
    return render(request, 'project_edit.html', context)

def criteria_list(request):

    criteria_list = PerformanceCriteria.objects.order_by('type')

    context = {
        'criteria_list': criteria_list,
        'page_title': "Danh mục tiêu chí"
    }

    return render(request, 'criteria_list.html', context)

def criteria_create(request):
    if request.method == 'POST':
        form = CriteriaCreateForm(request.POST)

        if form.is_valid():
            new_criteria = form.save()

            messages.success(request, f" Tiêu chí {new_criteria.name} đã được tạo thành công.")

            return redirect('criteria_list')

        else:
            messages.error(request, 'Có lỗi xảy ra trong quá trình tạo tiêu chí. Vui lòng kiểm tra lại thông tin.')

    else:
        form = CriteriaCreateForm()

    context = {
        'page_title': 'Tạo tiêu chí mới',
        'form': form
    }
    return render(request, 'criteria_create.html', context)

def reward_list(request):

    reward_list = RewardList.objects.order_by('-rewarded_date')

    context = {
        'reward_list': reward_list,
        'page_title': "Danh sách khen thưởng"
    }

    return render(request, 'reward_list.html', context)

def reward_suggest_list(request):

    reward_suggest_list = RewardSuggest.objects.order_by('-suggested_date')

    context = {
        'reward_suggest_list': reward_suggest_list,
        'page_title': 'Lịch sử đề xuất khen thưởng'
    }

    return render(request, 'reward_suggest_list.html', context)


def reward_suggest_form(request):
    if request.method == "POST":
        form = RewardSuggestForm(request.POST)

        if form.is_valid():
            new_reward_suggest = form.save()

            messages.success(request, f"Đề xuất khen thưởng {new_reward_suggest.fullname} đã được gửi thành công.")

            return redirect('reward_suggest_list')

    else:
        form = RewardSuggestForm()

    context = {
        'page_title': 'Đề xuất khen thưởng',
        'form': form
    }
    return render(request, 'reward_suggest_form.html', context)

def reward_announce_list(request):

    reward_announce_list = RewardAnnounce.objects.order_by('-announced_date')

    context = {
        'reward_announce_list': reward_announce_list,
        'page_title': 'Thông báo khen thưởng'
    }

    return render(request, 'reward_announce_list.html', context)
