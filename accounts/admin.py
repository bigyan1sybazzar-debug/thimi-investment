from django.contrib import admin
from .models import Member, GlobalSetting

admin.site.register(Member)
admin.site.register(GlobalSetting)