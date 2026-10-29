import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'
import router from '@/router'
import { authApi } from '@/api'

const STORAGE_KEYS = { user: 'user', accessToken: 'accessToken', refreshToken: 'refreshToken' }

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.user))
  } catch {
    return null
  }
}

function describeError(error, fallback) {
  const data = error.response?.data
  if (data?.details) return Object.values(data.details).flat().join('；')
  return data?.message || fallback
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref(readStoredUser())
  const accessToken = ref(localStorage.getItem(STORAGE_KEYS.accessToken))
  const refreshToken = ref(localStorage.getItem(STORAGE_KEYS.refreshToken))

  const status = reactive({ loggingIn: false, loginError: null, registering: false, registerError: null })

  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value))
  const userDisplayName = computed(() => user.value?.display_name || user.value?.username || '訪客')
  const userRole = computed(() => user.value?.role)
  const isAdmin = computed(() => userRole.value === 'admin')
  const isCoach = computed(() => userRole.value === 'coach')
  const isCadre = computed(() => userRole.value === 'cadre')

  function setUser(value) {
    user.value = value
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(value))
  }

  function setSession({ user: newUser, access_token: access, refresh_token: refresh }) {
    setUser(newUser)
    accessToken.value = access
    localStorage.setItem(STORAGE_KEYS.accessToken, access)
    if (refresh) {
      refreshToken.value = refresh
      localStorage.setItem(STORAGE_KEYS.refreshToken, refresh)
    }
  }

  function clearSession() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key))
  }

  async function login(credentials) {
    status.loggingIn = true
    status.loginError = null
    try {
      setSession(await authApi.login(credentials))
      return true
    } catch (error) {
      status.loginError = describeError(error, '登入失敗，請稍後再試。')
      return false
    } finally {
      status.loggingIn = false
    }
  }

  /** 註冊後直接登入。 */
  async function register(phoneNumber) {
    status.registering = true
    status.registerError = null
    try {
      setSession(await authApi.register(phoneNumber))
      return true
    } catch (error) {
      status.registerError = describeError(error, '註冊失敗，請稍後再試。')
      return false
    } finally {
      status.registering = false
    }
  }

  async function fetchCurrentUser() {
    if (!accessToken.value) return null
    try {
      setUser(await authApi.me())
      return user.value
    } catch {
      return null
    }
  }

  /** 換發 access token；失敗時登出。由 apiClient 在收到 401 時呼叫。 */
  async function refreshTokenAction() {
    if (!refreshToken.value) {
      logoutAndRedirect()
      return null
    }
    try {
      const { access_token: access } = await authApi.refresh(refreshToken.value)
      accessToken.value = access
      localStorage.setItem(STORAGE_KEYS.accessToken, access)
      return access
    } catch {
      logoutAndRedirect()
      return null
    }
  }

  function logoutAndRedirect() {
    clearSession()
    router.push({ name: 'Login', query: { loggedOut: 'true' } })
  }

  return {
    user,
    accessToken,
    status,
    isAuthenticated,
    userDisplayName,
    userRole,
    isAdmin,
    isCoach,
    isCadre,
    setUser,
    login,
    register,
    fetchCurrentUser,
    refreshTokenAction,
    logoutAndRedirect,
    clearLoginError: () => (status.loginError = null)
  }
})
