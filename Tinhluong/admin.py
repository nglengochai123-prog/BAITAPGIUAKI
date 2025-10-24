from django.contrib import admin
from Tinhluong.models import (Employee, SalaryComponent, Timesheet, CustomAdjustment, PayrollRecord)


admin.site.register(Employee)
admin.site.register(SalaryComponent)
admin.site.register(Timesheet)
admin.site.register(CustomAdjustment)
admin.site.register(PayrollRecord)

