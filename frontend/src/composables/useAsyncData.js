// src/composables/useAsyncData.js
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/services/apiClient'

/**
 * 統一異步操作管理 Composable
 * 統一處理 loading、error 狀態、API 調用和數據預處理
 */
export function useAsyncData(initialData = null) {
  const message = useMessage()

  // 狀態管理
  const loading = ref(false)
  const error = ref(null)
  const data = ref(initialData)

  // ========== 通用數據預處理函數 ==========

  // 日期格式化：時間戳 → 'YYYY-MM-DD'
  const formatDate = timestamp => {
    if (!timestamp) return null
    const date = new Date(timestamp)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }

  // 清理空字符串為 null
  const cleanEmptyStrings = obj => {
    const cleaned = { ...obj }
    Object.keys(cleaned).forEach(key => {
      if (cleaned[key] === '') {
        cleaned[key] = null
      }
    })
    return cleaned
  }

  // 成員數據預處理器
  const processMemberData = formData => {
    // 基礎數據結構
    const processed = {
      name: formData.name,
      display_name: formData.display_name || formData.name, // 自動默認值
      username: formData.username,
      password: formData.password || null,
      email: formData.email || null,
      role: formData.role,
      student_id: formData.student_id || null,
      gender: formData.gender,
      position: formData.position,
      organization_id: formData.organization_id,
      is_active: formData.is_active,
      notes: formData.notes,
      joined_date: formatDate(formData.joined_date_ts)
    }

    // 清理空字符串
    return cleanEmptyStrings(processed)
  }

  // 組織數據預處理器
  const processOrganizationData = formData => {
    return cleanEmptyStrings({
      name: formData.name,
      short_name: formData.short_name || null,
      description: formData.description || null,
      contact_person: formData.contact_person || null,
      contact_email: formData.contact_email || null,
      contact_phone: formData.contact_phone || null
    })
  }

  // 比賽數據預處理器
  const processMatchData = formData => {
    const processed = {
      ...formData,
      match_date: formatDate(formData.match_date_ts),
      // 清理其他可能的時間戳字段
      created_at: formatDate(formData.created_at_ts)
    }

    // 移除原始時間戳字段
    delete processed.match_date_ts
    delete processed.created_at_ts

    return cleanEmptyStrings(processed)
  }

  // ========== 數據預處理器映射 ==========
  const dataProcessors = {
    member: processMemberData,
    organization: processOrganizationData,
    match: processMatchData
    // 可以繼續添加其他類型
  }

  // ========== 通用的異步執行函數 ==========
  const execute = async (asyncFunction, options = {}) => {
    const {
      showLoading = true,
      showSuccess = true,
      showError = true,
      successMessage,
      errorMessage,
      onSuccess,
      onError,
      onFinally
    } = options

    if (showLoading) loading.value = true
    error.value = null

    try {
      const result = await asyncFunction()

      // 儲存數據
      if (result?.data !== undefined) {
        data.value = result.data
      }

      // 成功處理
      if (onSuccess) {
        await onSuccess(result)
      }

      if (successMessage && showSuccess) {
        message.success(successMessage)
      }

      return result
    } catch (err) {
      // 錯誤處理
      error.value = err.response?.data?.message || errorMessage || '操作失敗'

      if (onError) {
        await onError(err)
      }

      if (showError) {
        message.error(error.value)
      }

      throw err
    } finally {
      if (showLoading) loading.value = false

      if (onFinally) {
        await onFinally()
      }
    }
  }

  // ========== 增強的 HTTP 方法 ==========

  const get = (url, options = {}) => {
    return execute(() => apiClient.get(url), options)
  }

  // 智能 POST - 自動數據預處理
  const post = (url, payload = {}, options = {}) => {
    const { dataType, processor, ...executeOptions } = options

    let processedPayload = payload

    // 自動數據預處理
    if (dataType && dataProcessors[dataType]) {
      processedPayload = dataProcessors[dataType](payload)
      console.log(`🔧 ${dataType} 數據預處理完成:`, processedPayload)
    } else if (processor && typeof processor === 'function') {
      processedPayload = processor(payload)
      console.log('🔧 自定義數據預處理完成:', processedPayload)
    }

    return execute(() => apiClient.post(url, processedPayload), executeOptions)
  }

  // 智能 PUT - 自動數據預處理
  const put = (url, payload = {}, options = {}) => {
    const { dataType, processor, ...executeOptions } = options

    let processedPayload = payload

    // 自動數據預處理
    if (dataType && dataProcessors[dataType]) {
      processedPayload = dataProcessors[dataType](payload)
      console.log(`🔧 ${dataType} 數據預處理完成:`, processedPayload)
    } else if (processor && typeof processor === 'function') {
      processedPayload = processor(payload)
      console.log('🔧 自定義數據預處理完成:', processedPayload)
    }

    return execute(() => apiClient.put(url, processedPayload), executeOptions)
  }

  const del = (url, options = {}) => {
    return execute(() => apiClient.delete(url), options)
  }

  // ========== 特殊的業務方法 ==========

  // 成員相關 API
  const createMember = (memberData, options = {}) => {
    return post('/members', memberData, {
      dataType: 'member',
      successMessage: '成員已成功新增！',
      ...options
    })
  }

  const updateMember = (memberId, memberData, options = {}) => {
    return put(`/members/${memberId}`, memberData, {
      dataType: 'member',
      successMessage: '成員資料已成功更新！',
      ...options
    })
  }

  // 組織相關 API
  const createOrganization = (orgData, options = {}) => {
    return post('/organizations', orgData, {
      dataType: 'organization',
      successMessage: '組織已成功新增！',
      ...options
    })
  }

  const updateOrganization = (orgId, orgData, options = {}) => {
    return put(`/organizations/${orgId}`, orgData, {
      dataType: 'organization',
      successMessage: '組織已成功更新！',
      ...options
    })
  }

  // 比賽相關 API
  const createMatch = (matchData, options = {}) => {
    return post('/matches', matchData, {
      dataType: 'match',
      successMessage: '比賽記錄已成功新增！',
      ...options
    })
  }

  // ========== 工具方法 ==========

  // 重置狀態
  const reset = () => {
    loading.value = false
    error.value = null
    data.value = initialData
  }

  // 清除錯誤
  const clearError = () => {
    error.value = null
  }

  // 註冊自定義數據預處理器
  const registerProcessor = (type, processorFunction) => {
    dataProcessors[type] = processorFunction
  }

  return {
    // 狀態
    loading,
    error,
    data,

    // 基礎方法
    execute,
    get,
    post,
    put,
    del,

    // 業務特定方法
    createMember,
    updateMember,
    createOrganization,
    updateOrganization,
    createMatch,

    // 數據處理工具
    formatDateForAPI: formatDate,
    cleanEmptyStrings,
    processMemberData,
    processOrganizationData,
    processMatchData,
    registerProcessor,

    // 工具方法
    reset,
    clearError
  }
}
