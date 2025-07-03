from django.contrib import admin
from .models import User,Employer,AdminUser,JobPost,JobApplication

admin.site.register(User)
admin.site.register(Employer)
admin.site.register(AdminUser)
admin.site.register(JobPost)
admin.site.register(JobApplication)


# Register your models here.
