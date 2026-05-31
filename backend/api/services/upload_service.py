import time

from django.conf import settings
from django.db import close_old_connections

from ..models import UploadTask, KnowledgePoint
from common.upload_progress import set_upload_progress
from .ai_server_client import (
    upload_file_to_ai_server,
    poll_ai_server_progress,
)
from .ai_server_ws_client import ask_ai_server_for_knowledge_mapping


def process_upload_task(task_id):
    close_old_connections()

    try:
        task = UploadTask.objects.get(id=task_id)

        task.status = "PROCESSING"
        task.save(update_fields=["status", "updated_at"])

        set_upload_progress(task_id, "PROCESSING", "正在上传文件到 AI 服务", 20)

        ai_upload_result = upload_file_to_ai_server(
            file_path=task.file.path,
            filename=task.original_name,
            kb_name=settings.AI_SERVER_KB_NAME,
        )

        ai_task_id = ai_upload_result.get("task_id")

        set_upload_progress(
            task_id,
            "PROCESSING",
            f"AI 服务已接收文件，任务ID：{ai_task_id}",
            35
        )

        # 等待 ai-server 完成文档解析和索引
        while True:
            progress = poll_ai_server_progress(settings.AI_SERVER_KB_NAME)

            stage = progress.get("stage")
            message = progress.get("message", "")
            percent = progress.get("progress_percent") or 0

            # 把 ai-server 的 0-100 映射到 Django 的 35-80
            django_percent = 35 + int(percent * 0.45)

            set_upload_progress(
                task_id,
                "PROCESSING",
                f"AI 服务处理中：{message}",
                django_percent
            )

            if stage == "completed":
                break

            if stage == "error":
                raise RuntimeError(message or "AI 服务处理文件失败")

            time.sleep(2)

        set_upload_progress(task_id, "PROCESSING", "正在进行 AI 知识点映射", 85)

        knowledge_points_data = [
            {
                "id": point.id,
                "name": point.name,
                "category": point.category,
                "keywords": point.keywords,
                "description": point.description,
            }
            for point in KnowledgePoint.objects.all()
        ]

        ai_mapping_result = ask_ai_server_for_knowledge_mapping(
            kb_name=settings.AI_SERVER_KB_NAME,
            knowledge_points=knowledge_points_data,
        )

        task.summary = ai_mapping_result.get("summary", "")
        task.mapped_points = ai_mapping_result.get("matched_points", [])
        task.status = "DONE"
        task.save(update_fields=["summary", "mapped_points", "status", "updated_at"])

        set_upload_progress(task_id, "DONE", "AI 知识点映射完成", 100)

    except Exception as e:
        UploadTask.objects.filter(id=task_id).update(
            status="FAILED",
            error_message=str(e)
        )

        set_upload_progress(
            task_id,
            "FAILED",
            f"处理失败：{str(e)}",
            100
        )

    finally:
        close_old_connections()