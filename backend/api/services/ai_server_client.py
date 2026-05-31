import time

import requests
from django.conf import settings


def _kb_exists(kb_name):
    """检查 ai-server 上知识库是否已存在。"""
    url = f"{settings.AI_SERVER_HTTP_BASE_URL}/api/v1/knowledge/list"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    kb_list = resp.json()
    return any(item.get("name") == kb_name for item in kb_list)


def _create_kb_and_upload(kb_name, file_path, filename):
    """创建新知识库并上传文件（一次请求完成创建+上传）。"""
    url = f"{settings.AI_SERVER_HTTP_BASE_URL}/api/v1/knowledge/create"

    with open(file_path, "rb") as f:
        data = {
            "name": kb_name,
        }
        files = {
            "files": (filename, f),
        }
        response = requests.post(url, data=data, files=files, timeout=180)

    response.raise_for_status()
    return response.json()


def _upload_to_existing_kb(kb_name, file_path, filename):
    """向已存在的知识库上传文件。"""
    url = f"{settings.AI_SERVER_HTTP_BASE_URL}/api/v1/knowledge/{kb_name}/upload"

    with open(file_path, "rb") as f:
        files = {
            "files": (filename, f)
        }
        response = requests.post(url, files=files, timeout=180)

    response.raise_for_status()
    return response.json()


def upload_file_to_ai_server(file_path, filename, kb_name="default"):
    """
    把 Django 接收到的文件转发给 ai-server 的知识库上传接口。
    如果 KB 不存在则自动创建。
    """
    if _kb_exists(kb_name):
        return _upload_to_existing_kb(kb_name, file_path, filename)
    else:
        return _create_kb_and_upload(kb_name, file_path, filename)


def poll_ai_server_progress(kb_name, timeout=300, poll_interval=3):
    """
    轮询 ai-server 的知识库处理进度，直到完成或失败。
    返回最终的进度信息。
    """
    url = f"{settings.AI_SERVER_HTTP_BASE_URL}/api/v1/knowledge/{kb_name}/progress"
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"AI 服务处理超时（{timeout}秒）")

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        progress = resp.json()

        stage = progress.get("stage", "")
        if stage in ("completed", "error"):
            return progress

        time.sleep(poll_interval)


def get_kb_detail(kb_name="default"):
    """
    获取知识库详情（文档数、状态等）。
    """
    url = f"{settings.AI_SERVER_HTTP_BASE_URL}/api/v1/knowledge/{kb_name}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()