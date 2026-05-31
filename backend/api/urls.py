from django.urls import path
from . import views

urlpatterns = [
    path("api/upload/", views.upload_file),
    path("api/upload/tasks/", views.upload_task_list),
    path("api/upload/tasks/<int:task_id>/progress/", views.upload_task_progress),
    path("api/upload/tasks/<int:task_id>/result/", views.upload_task_result),
]