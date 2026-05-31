from django.contrib import admin
from .models import KnowledgePoint


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    search_fields = ("name", "category", "keywords")
