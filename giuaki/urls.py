"""
URL configuration for giuaki project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. SỬA DÒNG NÀY:
    # Trang login PHẢI nằm ở '/login/' để khớp với settings.py
    path('login/', views.login, name='login'),

    # 2. XÓA DÒNG GÂY XUNG ĐỘT NÀY ĐI:
    # path('', views.login, name='login'),

    # Trang logout sẽ tự động dùng cài đặt trong settings.py
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ... các path khác ...
    path('hr/', views.welcome_view, name='welcome_hr'),
    path('manager/', views.welcome_view_manager, name='welcome_manager'),
    path('employee/', views.welcome_view_employee, name='welcome_employee'),
    path('', include('Quanlytuyendung.urls')),
    path('', include('Khenthuong.urls')),
    path('', include('Tinhluong.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
