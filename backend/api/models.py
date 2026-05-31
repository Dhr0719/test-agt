from django.db import models


class KnowledgePoint(models.Model):
    name = models.CharField(max_length=200, verbose_name="名称")
    description = models.TextField(blank=True, default="", verbose_name="描述")
    category = models.CharField(max_length=100, blank=True, default="", verbose_name="分类")
    keywords = models.TextField(blank=True, default="", verbose_name="关键词")

    class Meta:
        db_table = "knowledge_point"
        verbose_name = "知识点"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
