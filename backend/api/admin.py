from django.contrib import admin
from .models import KnowledgePoint, UploadTask


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    search_fields = ("name", "category", "keywords")


@admin.register(UploadTask)
class UploadTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("original_name", "summary", "error_message")
    readonly_fields = ("created_at", "updated_at")
