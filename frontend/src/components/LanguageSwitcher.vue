<template>
  <div class="language-switcher" ref="switcherRef">
    <button class="switcher-trigger" @click="toggleDropdown">
      {{ currentLabel }}
      <span class="caret">{{ open ? '▲' : '▼' }}</span>
    </button>
    <ul v-if="open" class="switcher-dropdown">
      <li
        v-for="loc in availableLocales"
        :key="loc.key"
        class="switcher-option"
        :class="{ active: loc.key === locale }"
        @click="switchLocale(loc.key)"
      >
        {{ loc.label }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { availableLocales } from '@/i18n/index.js'

const { locale } = useI18n()
const open = ref(false)
const switcherRef = ref(null)

const currentLabel = computed(() => {
  const found = availableLocales.find(l => l.key === locale.value)
  return found ? found.label : locale.value
})

const toggleDropdown = () => {
  open.value = !open.value
}

const switchLocale = (key) => {
  locale.value = key
  localStorage.setItem('locale', key)
  document.documentElement.lang = key
  open.value = false
}

const onClickOutside = (e) => {
  if (switcherRef.value && !switcherRef.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  document.documentElement.lang = locale.value
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
}

.switcher-trigger {
  background: transparent;
  color: var(--text-body);
  border: 1px solid var(--border-strong);
  padding: 4px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  border-radius: 6px;
  transition: border-color 0.2s, color 0.2s, opacity 0.2s;
}

.switcher-trigger:hover {
  border-color: var(--accent-2);
  color: var(--accent-2);
}

.caret {
  font-size: 0.6rem;
}

.switcher-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: var(--elevated);
  border: 1px solid var(--border);
  list-style: none;
  padding: 4px 0;
  min-width: 100%;
  z-index: 1000;
  border-radius: 8px;
  box-shadow: var(--shadow-md);
}

.switcher-option {
  padding: 6px 12px;
  font-size: 0.8rem;
  color: var(--text-body);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}

.switcher-option:hover {
  background: var(--surface-2);
}

.switcher-option.active {
  color: var(--accent);
}


</style>
