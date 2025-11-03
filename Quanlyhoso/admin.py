from django.contrib import admin
from .models import (PhongBan, ChucVu, NhanVien, HopDong, DonNghiPhep)

# Register your models here.
admin.site.register(PhongBan)
admin.site.register(ChucVu)
admin.site.register(NhanVien)
admin.site.register(HopDong)
admin.site.register(DonNghiPhep)