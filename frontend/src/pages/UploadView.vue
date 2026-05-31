<script setup>
import { ref } from "vue";

const selectedFile = ref(null);

function handleFileChange(event) {
  selectedFile.value = event.target.files[0];
}

function handleUpload() {
  if (!selectedFile.value) {
    alert("请先选择文件");
    return;
  }

  console.log("准备上传文件：", selectedFile.value);
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

      <button @click="handleUpload">
        上传并分析
      </button>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px;
}

.upload-box {
  margin-top: 16px;
  padding: 24px;
  border: 1px dashed #ccc;
  border-radius: 12px;
}

button {
  margin-top: 16px;
  padding: 8px 16px;
  cursor: pointer;
}
</style>