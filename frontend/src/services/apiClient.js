import axios from 'axios'

/**
 * 後端回應格式：
 *   成功 { data, meta?, message? }
 *   失敗 { error: { code, message, details? } }
 *
 * 攔截器會拆開外層：
 *   response.data    → 後端的 data
 *   response.meta    → 分頁等資訊（如果有）
 *   response.message → 後端訊息（如果有）
 *   error.response.data → 後端的 error 物件，所以 error.response.data.message 可直接使用
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const REFRESH_URL = '/auth/refresh'
// 這些請求回 401 代表帳密錯誤，不應嘗試刷新 token
const NO_REFRESH_URLS = [REFRESH_URL, '/auth/login', '/auth/register']

apiClient.interceptors.request.use(config => {
  // refresh 請求自行帶 refresh token，不要被 access token 覆蓋
  if (config.url !== REFRESH_URL) {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

apiClient.interceptors.response.use(
  response => {
    const body = response.data
    if (body && typeof body === 'object' && 'data' in body) {
      response.meta = body.meta
      response.message = body.message
      response.data = body.data
    }
    return response
  },
  async error => {
    const { config, response } = error
    if (response?.data?.error) {
      response.data = response.data.error
    }

    if (response?.status === 401 && config && !NO_REFRESH_URLS.includes(config.url) && !config._retried) {
      config._retried = true
      const { useAuthStore } = await import('@/stores/authStore.js')
      const newAccessToken = await useAuthStore().refreshTokenAction()
      if (newAccessToken) {
        config.headers.Authorization = `Bearer ${newAccessToken}`
        return apiClient(config)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
