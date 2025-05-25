from django.contrib import admin
from .models import *
from .models import Admin_Health_CSV
# Register your models here.

admin.site.register(Admin_Health_CSV)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Feedback)
admin.site.register(Search_Data)
