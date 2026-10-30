import { computed, ref, watchEffect } from 'vue'

const STORAGE_KEY = 'theme'

function readStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'dark' ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

// 全站共用同一個狀態；預設淺色
const theme = ref(readStoredTheme())

watchEffect(() => {
  document.documentElement.dataset.theme = theme.value
  try {
    localStorage.setItem(STORAGE_KEY, theme.value)
  } catch {
    // 無法存取 localStorage 時只在這次瀏覽有效
  }
})

/** 淺色／深色模式。 */
export function useTheme() {
  const isDark = computed(() => theme.value === 'dark')
  const toggleTheme = () => {
    theme.value = isDark.value ? 'light' : 'dark'
  }
  return { theme, isDark, toggleTheme }
}
