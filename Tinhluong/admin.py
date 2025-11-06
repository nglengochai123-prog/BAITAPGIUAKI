from django.contrib import admin
from .models import (SalaryComponent, EmployeeSalary, PayrollPeriod, Timekeeping, VariableBonus, PayrollEntry)


admin.site.register(SalaryComponent)
admin.site.register(EmployeeSalary)
admin.site.register(PayrollPeriod)
admin.site.register(Timekeeping)
admin.site.register(VariableBonus)
admin.site.register(PayrollEntry)
