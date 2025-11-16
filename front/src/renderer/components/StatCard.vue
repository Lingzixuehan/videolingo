<template>
  <div class="card stat">
    <span class="label">{{ label }}</span>
    <strong class="value">{{ value }}</strong>
    <small v-if="hint" class="hint">{{ hint }}</small>
  </div>
</template>
<script setup lang="ts">
defineProps<{ label:string; value:string|number; hint?:string }>();
</script>
<style scoped>
.stat { min-width:140px; position:relative; }
.label { display:block; font-size:12px; color:var(--c-text-dim); }
.value { font-size:22px; line-height:1.2; }
.hint { position:absolute; right:12px; bottom:8px; font-size:11px; color:var(--c-text-dim); }
</style>