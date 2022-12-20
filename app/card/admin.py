from django.contrib import admin

from .models import Card, Audio, Video, Report

# Register your models here.

admin.site.register(Card)
admin.site.register(Audio)
admin.site.register(Video)
admin.site.register(Report)