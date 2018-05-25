from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(Manage)
admin.site.register(RecurringTask)
admin.site.register(Note)
admin.site.register(Feedback)




