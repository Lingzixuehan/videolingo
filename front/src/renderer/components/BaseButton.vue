<template>
  <button
    :class="['btn', variant || '', { small }]"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>
<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'danger' | '';
  disabled?: boolean;
  small?: boolean;
}>();
</script>
<style scoped>
.btn.small { padding:4px 10px; font-size:12px; }
.btn:disabled { opacity:.55; cursor:not-allowed; }
</style>