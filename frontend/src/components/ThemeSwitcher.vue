<template>
  <button
    class="theme-switcher"
    :title="resolvedTheme === 'dark' ? $t('theme.switchToLight') : $t('theme.switchToDark')"
    :aria-label="resolvedTheme === 'dark' ? $t('theme.switchToLight') : $t('theme.switchToDark')"
    @click="toggleTheme"
  >
    <!-- Sun (shown in dark mode → click to go light) -->
    <svg v-if="resolvedTheme === 'dark'" class="ts-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
    </svg>
    <!-- Moon (shown in light mode → click to go dark) -->
    <svg v-else class="ts-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  </button>
</template>

<script setup>
import { useTheme } from '@/store/theme.js'

const { resolvedTheme, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-switcher {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  width: var(--header-control-height, 32px);
  height: var(--header-control-height, 32px);
  margin: 0;
  padding: 0;
  flex-shrink: 0;
  background: transparent;
  color: var(--text-muted, #666);
  border: 1px solid var(--border-strong, #ccc);
  border-radius: var(--header-control-radius, 6px);
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
}

.theme-switcher:hover {
  color: var(--accent-2, #6d5bff);
  border-color: var(--accent-2, #6d5bff);
}

.ts-icon {
  width: 16px;
  height: 16px;
}
</style>
