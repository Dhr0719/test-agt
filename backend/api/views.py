import threading

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from .models import UploadTask
from .services.upload_service import process_upload_task
from common.upload_progress import set_upload_progress, get_upload_progress


@csrf_exempt
def upload_file(request):
    if request.method != "POST":
        return JsonResponse({
            "code": 405,
            "msg": "只支持 POST 请求",
        })

    file = request.FILES.get("file")

    if not file:
        return JsonResponse({
            "code": 400,
            "msg": "请上传文件",
        })

    task = UploadTask.objects.create(
        original_name=file.name,
        file=file,
        status="PENDING",
    )

    set_upload_progress(task.id, "PENDING", "任务已创建，等待处理", 0)

    thread = threading.Thread(
        target=process_upload_task,
        args=(task.id,),
        daemon=True
    )
    thread.start()

    return JsonResponse({
        "code": 0,
        "msg": "上传成功，正在分析",
        "data": {
            "task_id": task.id,
            "status": task.status,
            "original_name": task.original_name,
        }
    })


def upload_task_list(request):
    tasks = UploadTask.objects.all().order_by("-created_at")

    data = []
    for task in tasks:
        data.append({
            "task_id": task.id,
            "original_name": task.original_name,
            "status": task.status,
            "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": data,
    })


def upload_task_progress(request, task_id):
    data = get_upload_progress(task_id)

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": data,
    })


def upload_task_result(request, task_id):
    try:
        task = UploadTask.objects.get(id=task_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": "任务不存在",
        })

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": {
            "task_id": task.id,
            "original_name": task.original_name,
            "status": task.status,
            "summary": task.summary,
            "mapped_points": task.mapped_points,
            "error_message": task.error_message,
        }
    })