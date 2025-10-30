<template>
  <div class="page">
    <h2>设置</h2>

    <section style="margin-top:12px;">
      <h3>下载</h3>
      <div style="display:flex; align-items:center; gap:8px;">
        <input v-model="cfg.downloadDir" style="width:420px" placeholder="下载目录" />
        <button @click="chooseDir">选择目录</button>
      </div>
    </section>

    <div style="margin-top:16px;">
      <button @click="save">保存</button>
      <span v-if="saved" style="margin-left:8px;color:green;">已保存</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
const cfg = reactive<{ downloadDir: string }>({ downloadDir: '' });
const saved = ref(false);

onMounted(async () => {
  const res = await window.api?.config.read();
  Object.assign(cfg, res ?? { downloadDir: '' });
});

async function chooseDir() {
  const res = await window.api?.pickDirectory?.();
  if (res && res.canceled === false && res.filePaths?.length) {
    cfg.downloadDir = res.filePaths[0];
  }
}

async function save() {
  await window.api?.config.write(cfg);
  saved.value = true; setTimeout(() => (saved.value = false), 1200);
}
</script>