<script setup>
import { onMounted } from "vue";
import { testBackend } from "@/api/test";

onMounted(() => {
  testBackend().then(res => {
    console.log(res);
  });
});
</script>