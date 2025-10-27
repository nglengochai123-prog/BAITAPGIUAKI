from django.contrib import admin
from .models import (SalaryComponent, EmployeeSalary, PayrollPeriod, ChamCong, VariableBonus, PayrollEntry)


admin.site.register(SalaryComponent)
admin.site.register(EmployeeSalary)
admin.site.register(PayrollPeriod)
admin.site.register(ChamCong)
admin.site.register(VariableBonus)
admin.site.register(PayrollEntry)
