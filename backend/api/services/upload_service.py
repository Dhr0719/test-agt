import time
from django.db import close_old_connections

from ..models import UploadTask, KnowledgePoint
from common.upload_progress import set_upload_progress


def extract_text_from_file(file_path):
    """
    第一版先支持 txt / md / py / java / c / cpp 这类文本文件。
    PDF、Word 后面再加解析库。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="gbk", errors="ignore") as f:
            return f.read()


def simple_match_knowledge_points(text, knowledge_points):
    """
    第一版先用关键词模拟知识点映射。
    后面这里可以替换成 DeepSeek 分析。
    """
    result = []
    lower_text = text.lower()

    for point in knowledge_points:
        keywords = point.keywords or ""
        keyword_list = [k.strip() for k in keywords.replace("，", ",").split(",") if k.strip()]

        matched_keywords = []

        if point.name and point.name.lower() in lower_text:
            matched_keywords.append(point.name)

        for keyword in keyword_list:
            if keyword.lower() in lower_text:
                matched_keywords.append(keyword)

        if matched_keywords:
            result.append({
                "knowledge_point_id": point.id,
                "name": point.name,
                "category": point.category,
                "confidence": 0.8,
                "reason": f"文件内容中匹配到关键词：{', '.join(set(matched_keywords))}",
            })

    return result


def process_upload_task(task_id):
    """
    后台处理上传任务。
    第一版：模拟进度 + 简单关键词匹配。
    """
    close_old_connections()

    try:
        task = UploadTask.objects.get(id=task_id)

        task.status = "PROCESSING"
        task.save(update_fields=["status", "updated_at"])
        set_upload_progress(task_id, "PROCESSING", "正在读取文件", 20)

        time.sleep(0.5)

        text = extract_text_from_file(task.file.path)
        set_upload_progress(task_id, "PROCESSING", "正在解析文件内容", 40)

        time.sleep(0.5)

        knowledge_points = KnowledgePoint.objects.all()
        set_upload_progress(task_id, "PROCESSING", "正在匹配知识点", 60)

        time.sleep(0.5)

        mapped_points = simple_match_knowledge_points(text, knowledge_points)

        task.summary = text[:300]
        task.mapped_points = mapped_points
        task.status = "DONE"
        task.save(update_fields=["summary", "mapped_points", "status", "updated_at"])

        set_upload_progress(task_id, "DONE", "分析完成", 100)

    except Exception as e:
        UploadTask.objects.filter(id=task_id).update(
            status="FAILED",
            error_message=str(e)
        )
        set_upload_progress(task_id, "FAILED", f"处理失败：{str(e)}", 100)

    finally:
        close_old_connections()