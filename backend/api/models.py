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


class UploadTask(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "待处理"),
        (STATUS_PROCESSING, "处理中"),
        (STATUS_DONE, "已完成"),
        (STATUS_FAILED, "失败"),
    ]

    original_name = models.CharField(max_length=500, verbose_name="原始文件名")
    file = models.FileField(upload_to="uploads/%Y/%m/%d/", verbose_name="文件路径")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="任务状态")
    summary = models.TextField(blank=True, default="", verbose_name="AI 总结")
    mapped_points = models.JSONField(blank=True, default=list, verbose_name="映射知识点")
    error_message = models.TextField(blank=True, default="", verbose_name="失败原因")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "upload_task"
        verbose_name = "上传任务"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_name
