<script setup>
import { ref } from "vue";
import {
  uploadFile,
  getUploadProgress,
  getUploadResult,
} from "@/api/upload";

const selectedFile = ref(null);
const taskId = ref(null);
const progress = ref({
  status: "IDLE",
  step: "等待上传",
  percent: 0,
});
const result = ref(null);
const loading = ref(false);
let timer = null;

function handleFileChange(event) {
  selectedFile.value = event.target.files[0];
  result.value = null;
  taskId.value = null;
  progress.value = {
    status: "IDLE",
    step: "等待上传",
    percent: 0,
  };
}

async function handleUpload() {
  if (!selectedFile.value) {
    alert("请先选择文件");
    return;
  }

  try {
    loading.value = true;

    const res = await uploadFile(selectedFile.value);

    if (res.code !== 0) {
      alert(res.msg || "上传失败");
      loading.value = false;
      return;
    }

    taskId.value = res.data.task_id;

    progress.value = {
      status: res.data.status,
      step: "任务已创建，正在分析",
      percent: 0,
    };

    startPollingProgress();
  } catch (error) {
    console.error(error);
    alert("上传失败，请检查后端服务");
    loading.value = false;
  }
}

function startPollingProgress() {
  if (timer) {
    clearInterval(timer);
  }

  timer = setInterval(async () => {
    try {
      const res = await getUploadProgress(taskId.value);

      if (res.code === 0) {
        progress.value = {
          status: res.data.status,
          step: res.data.step,
          percent: Number(res.data.percent || 0),
        };

        if (res.data.status === "DONE") {
          clearInterval(timer);
          timer = null;
          loading.value = false;
          await loadResult();
        }

        if (res.data.status === "FAILED") {
          clearInterval(timer);
          timer = null;
          loading.value = false;
          await loadResult();
        }
      }
    } catch (error) {
      console.error("获取进度失败：", error);
    }
  }, 1000);
}

async function loadResult() {
  if (!taskId.value) return;

  const res = await getUploadResult(taskId.value);

  if (res.code === 0) {
    result.value = res.data;
  }
}
</script>

<template>
  <div class="page">
    <h2>文件上传与知识点映射</h2>

    <div class="upload-box">
      <input type="file" @change="handleFileChange" />

      <p v-if="selectedFile">
        已选择：{{ selectedFile.name }}
      </p>

      <button @click="handleUpload" :disabled="loading">
        {{ loading ? "分析中..." : "上传并分析" }}
      </button>
    </div>

    <div class="progress-box" v-if="taskId">
      <h3>分析进度</h3>

      <p>任务ID：{{ taskId }}</p>
      <p>状态：{{ progress.status }}</p>
      <p>步骤：{{ progress.step }}</p>

      <div class="progress-bar">
        <div
          class="progress-inner"
          :style="{ width: progress.percent + '%' }"
        ></div>
      </div>

      <p>{{ progress.percent }}%</p>
    </div>

    <div class="result-box" v-if="result">
      <h3>分析结果</h3>

      <p>文件名：{{ result.original_name }}</p>
      <p>状态：{{ result.status }}</p>

      <h4>摘要</h4>
      <p>{{ result.summary || "暂无摘要" }}</p>

      <h4>映射知识点</h4>

      <div v-if="result.mapped_points && result.mapped_points.length">
        <div
          v-for="item in result.mapped_points"
          :key="item.knowledge_point_id"
          class="point-card"
        >
          <strong>{{ item.name }}</strong>
          <p>分类：{{ item.category }}</p>
          <p>置信度：{{ item.confidence }}</p>
          <p>原因：{{ item.reason }}</p>
        </div>
      </div>

      <p v-else>暂未匹配到知识点</p>

      <p v-if="result.error_message" class="error">
        错误信息：{{ result.error_message }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px;
}

.upload-box,
.progress-box,
.result-box {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

button {
  margin-top: 12px;
  padding: 8px 16px;
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.progress-bar {
  width: 300px;
  height: 12px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  background: #2563eb;
  transition: width 0.3s;
}

.point-card {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.error {
  color: red;
}
</style>