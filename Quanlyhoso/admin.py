from django.contrib import admin
from .models import (Department, Position, Employee, Contract, LeaveApplication)

# Register your models here.
admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Employee)
admin.site.register(Contract)
admin.site.register(LeaveApplication)