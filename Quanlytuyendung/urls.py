from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

#URL DÀNH CHO ỨNG VIÊN - VÃNG LAI

    path('recruitment/apply/', views.candidate_apply, name='candidate_apply'), #Ứng viên
    path('recruitment/', views.recruitment_home, name='recruitment_home'), #Ứng viên
    path('recruitment/recruitment-post/', views.all_job_postings, name='all_job_postings'), #Ứng viên
    path('recruitment/recruitment-post/<int:pk>/', views.recruitment_post_detail, name='recruitment_post_detail'), # Ứng viên

#URL DÀNH CHO HR
    #Trang quản lý tuyển dụng chung cho toàn bộ yếu tố
    path('hr/recruitment/recruitment-management/', views.quanly_tuyendung, name='quanly_tuyendung'), #HR

    #Các trang quản lý bài đăng tuyển dụng dành riêng cho HR
    path('hr/recruitment/recruitment-management/recruitment-post-hr/', views.all_job_postings_hr, name='all_job_postings_hr'),
    path('hr/recruitment/recruitment-management/edit-bd/<int:pk>/', views.edit_recruitment_post, name='edit_recruitment_post'),
    path('hr/recruitment/recruiment-management/delete-bd/<int:pk>/', views.delete_recruitment_post, name='delete_recruitment_post'),
    #path('hr/td/quanlytd/baidangtuyendunghr/create/', views.create_recruitment_post, name='create_recruitment_post'), #HR

    #Các trang quản lý trạng thái tuyển dụng ứng viên của HR + xóa ứng viên
    path('hr/recruitment/recruitment-management/manage-status/', views.manage_status, name='manage_status'), #HR
    path('hr/recruitment/recruitment-management/manage-status/candidate/<int:pk>/', views.view_candidate, name='view_candidate'), #HR
    path('hr/recruitment/recruitment-management/delete-candidate/<int:candidate_id>/', views.delete_candidate, name='delete_candidate'), #HR
    path('hr/recruitment/recruitment-management/edit-status/<int:candidate_id>/', views.edit_status, name='edit_status'), #HR

    #Các trang quản lý Skill cần có của ứng viên
    path('hr/recruitment/recruitment-management/add-skill/', views.add_skill, name='add_skill'), #HR
    path('hr/recruitment/recruitment-management/delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'), #HR

    #Trang xét duyệt yêu cầu tuyển dụng của HR đối với quản lý
    path('hr/recruitment/recruitment-management/manage-requests/', views.manage_requests_hr, name='manage_requests_hr'), #HR

#URL DÀNH CHO QUẢN LÝ

    #Trang quản lý yêu cầu tuyển dụng của quản lý
    path('manager/recruitment/all-requests/', views.all_recruitment_requests_manager, name='all_recruitment_requests_manager'), #Quản lý
    path('manager/recruitment/edit-request/<int:request_id>/', views.edit_recruitment_request, name='edit_recruitment_request'), #Quản lý
    path('manager/recruitment/delete-request/<int:request_id>/', views.delete_recruitment_request, name='delete_recruitment_request'), #Quản lý
]