<script setup lang="ts">
withDefaults(defineProps<{ name?: string }>(), {
  name: "Neo"
});
</script>

<template>
  <div
    class="fixed bottom-4 right-4 z-50 flex flex-col items-center pointer-events-none select-none">
    <span class="text-5xl animate-cat-bounce">🐈</span>
    <span class="mt-1 text-xs font-medium text-muted">{{ name }}</span>
  </div>
</template>
