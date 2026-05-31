import request from "@/utils/request";

/**
 * 上传文件并创建分析任务
 */
export function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request.post("/api/upload/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

/**
 * 获取上传任务列表
 */
export function getUploadTasks() {
  return request.get("/api/upload/tasks/");
}

/**
 * 获取任务进度
 */
export function getUploadProgress(taskId) {
  return request.get(`/api/upload/tasks/${taskId}/progress/`);
}

/**
 * 获取分析结果
 */
export function getUploadResult(taskId) {
  return request.get(`/api/upload/tasks/${taskId}/result/`);
}