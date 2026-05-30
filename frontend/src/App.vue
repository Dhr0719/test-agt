<script setup>
import { onMounted, ref } from 'vue'

const msg = ref('')

onMounted(async () => {
  const res = await fetch('http://127.0.0.1:8000/api/hello/')
  const data = await res.json()
  msg.value = data.msg
})
</script>

<template>
  <h1>{{ msg }}</h1>
</template>