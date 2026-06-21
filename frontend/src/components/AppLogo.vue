<template>
  <img
    src="/logo.png"
    alt="Digital Twin Agent Sandbox"
    class="app-logo"
    :class="size"
  />
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
})
</script>

<style scoped>
.app-logo {
  display: block;
  width: auto;
  object-fit: contain;
  flex-shrink: 0;
}

.app-logo.sm {
  height: 24px;
}

.app-logo.md {
  height: 32px;
}

.app-logo.lg {
  height: 40px;
}
</style>
