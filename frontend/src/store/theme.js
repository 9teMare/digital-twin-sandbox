/*
  Theme store — light / dark / system with persistence.

  - mode: 'system' | 'light' | 'dark'  (persisted)
  - resolvedTheme: 'light' | 'dark'    (what is actually applied)
  - When mode === 'system', follows the OS preference live.
  - A manual toggle sets an explicit mode (remembered across sessions).
*/

import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'dtas-theme-mode'

const stored = typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null
const mode = ref(stored === 'light' || stored === 'dark' || stored === 'system' ? stored : 'system')

const mql = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-color-scheme: dark)')
  : null
const systemDark = ref(mql ? mql.matches : false)

if (mql) {
  const onChange = (e) => { systemDark.value = e.matches }
  if (mql.addEventListener) mql.addEventListener('change', onChange)
  else if (mql.addListener) mql.addListener(onChange)
}

const resolvedTheme = computed(() =>
  mode.value === 'system' ? (systemDark.value ? 'dark' : 'light') : mode.value
)

function apply() {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute('data-theme', resolvedTheme.value)
}

watch(resolvedTheme, apply)

function setMode(next) {
  mode.value = next
  try { localStorage.setItem(STORAGE_KEY, next) } catch (e) { /* ignore */ }
}

function toggleTheme() {
  setMode(resolvedTheme.value === 'dark' ? 'light' : 'dark')
}

function initTheme() {
  apply()
}

export function useTheme() {
  return { mode, resolvedTheme, systemDark, setMode, toggleTheme, initTheme }
}
