<template>
  <div class="member-form-page">
    <!-- 載入狀態 -->
    <div v-if="isLoading" class="loading-container">
      <n-spin size="large">
        <template #description>
          <n-text depth="2">{{ mode === 'edit' ? '載入成員資料...' : '準備中...' }}</n-text>
        </template>
      </n-spin>
    </div>

    <!-- 錯誤狀態 -->
    <n-alert
      v-else-if="fetchError"
      title="載入失敗"
      type="error"
      closable
      class="error-alert"
      @close="fetchError = null"
    >
      {{ fetchError }}
    </n-alert>

    <!-- 主要內容 -->
    <div v-else class="form-container">
      <!-- 現代化頁面標題 -->
      <div class="page-header">
        <div class="header-content">
          <n-button text class="back-button" :focusable="false" @click="goBack">
            <template #icon>
              <n-icon :component="ArrowBackIcon" />
            </template>
          </n-button>

          <div class="title-section">
            <h1 class="page-title">
              {{ pageTitle }}
              <!-- 訪客標籤 -->
              <n-tag v-if="isGuestMember" type="warning" size="small" round class="guest-tag">
                <template #icon>
                  <n-icon :component="PersonIcon" />
                </template>
                訪客
              </n-tag>
            </h1>
            <p class="page-subtitle">{{ pageSubtitle }}</p>
          </div>
        </div>
      </div>

      <!-- 現代化表單卡片 -->
      <n-card class="form-card" :bordered="false">
        <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="top" @submit.prevent="handleSubmit">
          <!-- 錯誤提示 -->
          <n-alert
            v-if="submitMessage"
            :title="submitStatus === 'success' ? '操作成功' : '操作失敗'"
            :type="submitStatus"
            closable
            class="submit-alert"
            @close="clearSubmitMessage"
          >
            {{ submitMessage }}
          </n-alert>

          <!-- 基本資訊區塊 -->
          <div class="form-section">
            <div class="section-header">
              <n-icon :component="PersonCircleIcon" class="section-icon" />
              <h3 class="section-title">基本資訊</h3>
            </div>

            <n-grid :x-gap="24" :y-gap="16" :cols="12" item-responsive>
              <n-form-item-gi :span="12" :md="6" label="真實姓名" path="name">
                <n-input v-model:value="formData.name" placeholder="請輸入成員的真實姓名" size="large" />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="顯示名稱" path="display_name">
                <n-input
                  v-model:value="formData.display_name"
                  placeholder="排行榜顯示名稱（預設同真實姓名）"
                  size="large"
                />
              </n-form-item-gi>
            </n-grid>
          </div>

          <!-- 帳號資訊區塊（非訪客才顯示） -->
          <div v-if="!isGuestMember" class="form-section">
            <div class="section-header">
              <n-icon :component="KeyIcon" class="section-icon" />
              <h3 class="section-title">登入帳號</h3>
              <n-text depth="3" class="section-description">用於系統登入的帳號資訊</n-text>
            </div>

            <n-grid :x-gap="24" :y-gap="16" :cols="12" item-responsive>
              <n-form-item-gi :span="12" :md="6" label="手機號碼" path="username">
                <n-input v-model:value="formData.username" placeholder="09xxxxxxxx" size="large" />
              </n-form-item-gi>

              <n-form-item-gi v-if="mode === 'add'" :span="12" :md="6" label="初始密碼" path="password">
                <n-input
                  v-model:value="formData.password"
                  type="password"
                  placeholder="留空則使用手機號碼"
                  show-password-on="click"
                  size="large"
                />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="電子郵件" path="email">
                <n-input v-model:value="formData.email" placeholder="example@example.com（選填）" size="large" />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="角色權限" path="role">
                <n-select
                  v-model:value="formData.role"
                  :options="filteredRoleOptions"
                  placeholder="選擇角色"
                  size="large"
                />
              </n-form-item-gi>
            </n-grid>
          </div>

          <!-- 球員資料區塊 -->
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">球員資料</h3>
            </div>

            <n-grid :x-gap="24" :y-gap="16" :cols="12" item-responsive>
              <n-form-item-gi :span="12" :md="6" label="學號" path="student_id">
                <n-input v-model:value="formData.student_id" placeholder="學生證號碼（選填）" size="large" />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="性別" path="gender">
                <n-select
                  v-model:value="formData.gender"
                  :options="genderOptions"
                  placeholder="選擇性別"
                  clearable
                  size="large"
                />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="慣用位置" path="position">
                <n-select
                  v-model:value="formData.position"
                  :options="positionOptions"
                  placeholder="前排/後排/皆可"
                  clearable
                  size="large"
                />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="所屬組織" path="organization_id">
                <n-select
                  v-model:value="formData.organization_id"
                  :options="organizationOptions"
                  placeholder="選擇組織單位"
                  clearable
                  filterable
                  size="large"
                />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="入隊日期" path="joined_date_ts">
                <n-date-picker
                  v-model:value="formData.joined_date_ts"
                  type="date"
                  clearable
                  size="large"
                  style="width: 100%"
                />
              </n-form-item-gi>

              <n-form-item-gi v-if="mode === 'edit'" :span="12" :md="6" label="離隊日期" path="leaved_date_ts">
                <n-date-picker
                  v-model:value="formData.leaved_date_ts"
                  type="date"
                  clearable
                  size="large"
                  style="width: 100%"
                />
              </n-form-item-gi>

              <n-form-item-gi :span="12" :md="6" label="狀態">
                <div class="status-toggle">
                  <n-switch v-model:value="formData.is_active" size="large">
                    <template #checked>現役</template>
                    <template #unchecked>非現役</template>
                  </n-switch>
                </div>
              </n-form-item-gi>

              <n-form-item-gi :span="12" label="備註" path="notes">
                <n-input
                  v-model:value="formData.notes"
                  type="textarea"
                  placeholder="其他備註資訊（選填）"
                  :autosize="{ minRows: 3, maxRows: 6 }"
                  size="large"
                />
              </n-form-item-gi>
            </n-grid>
          </div>

          <!-- 動作按鈕 -->
          <div class="action-section">
            <n-space justify="end" :size="16">
              <n-button size="large" :disabled="submitting" @click="goBack"> 取消 </n-button>

              <n-button type="primary" attr-type="submit" :loading="submitting" size="large" strong>
                <template #icon>
                  <n-icon :component="mode === 'add' ? AddIcon : SaveIcon" />
                </template>
                {{ submitButtonText }}
              </n-button>
            </n-space>
          </div>
        </n-form>
      </n-card>
    </div>
  </div>
</template>

<script setup>
  import { computed, onMounted, reactive, ref, watch } from 'vue'

  import { useOptions, useAsyncData } from '@/composables'
  import {
    NAlert,
    NButton,
    NCard,
    NDatePicker,
    NForm,
    NFormItemGi,
    NGi,
    NGrid,
    NIcon,
    NInput,
    NInputNumber,
    NSelect,
    NSpace,
    NSpin,
    NSwitch,
    NTag,
    NText,
    useMessage
  } from 'naive-ui'
  import {
    ArrowBackOutline as ArrowBackIcon,
    PersonCircleOutline as PersonCircleIcon,
    PersonOutline as PersonIcon,
    KeyOutline as KeyIcon,
    AddOutline as AddIcon,
    SaveOutline as SaveIcon
  } from '@vicons/ionicons5'
  import { useRouter } from 'vue-router'

  // Props
  const props = defineProps({
    mode: {
      type: String,
      default: 'add',
      validator: value => ['add', 'edit'].includes(value)
    },
    id: {
      type: [String, Number],
      default: null
    }
  })

  // Composables
  const router = useRouter()
  const message = useMessage()
  const {
    genderOptions,
    positionOptions,
    organizationOptions,
    loadOrganizationOptions,
    getRoleOptionsForUser,
    isValidOption
  } = useOptions()

  const { loading: submitting, createMember, updateMember, get: fetchData } = useAsyncData()

  // State
  const formRef = ref(null)
  const isLoading = ref(false)
  const fetchError = ref(null)
  const submitMessage = ref('')
  const submitStatus = ref('')

  const formData = reactive({
    id: null,
    name: '',
    display_name: '',
    username: '',
    password: '',
    email: '',
    role: 'member',
    student_id: '',
    gender: null,
    position: null,
    organization_id: null,
    is_active: true,
    joined_date_ts: null,
    leaved_date_ts: null,
    notes: '',
    mu: null,
    sigma: null
  })

  // Computed
  const pageTitle = computed(() => {
    if (props.mode === 'edit') {
      return formData.name ? `編輯 ${formData.name}` : '編輯成員'
    }
    return '新增球隊成員'
  })

  const pageSubtitle = computed(() => {
    if (props.mode === 'edit') {
      return '修改成員的基本資料和權限設定'
    }
    return '建立新的球隊成員帳號和基本資料'
  })

  const isGuestMember = computed(() => formData.role === 'guest')

  const filteredRoleOptions = computed(() => getRoleOptionsForUser('non-admin'))

  const submitButtonText = computed(() => {
    if (submitting.value) {
      return props.mode === 'add' ? '新增中...' : '儲存中...'
    }
    return props.mode === 'add' ? '確認新增' : '確認更新'
  })

  // Form Rules
  const formRules = computed(() => {
    const baseRules = {
      name: [{ required: true, message: '真實姓名為必填', trigger: ['blur', 'input'] }],
      email: [{ type: 'email', message: '請輸入有效的電子郵件格式', trigger: ['blur', 'input'] }],
      student_id: [
        {
          required: false,
          trigger: ['blur', 'input'],
          validator: (rule, value) => {
            if (value && !/^\d{7,9}$/.test(value)) return new Error('學號必須是7到9位數字')
            return true
          }
        }
      ]
    }

    // 如果不是訪客，則需要手機號碼和角色驗證
    if (!isGuestMember.value) {
      baseRules.username = [
        { required: true, message: '手機號碼為必填', trigger: ['blur', 'input'] },
        { pattern: /^09\d{8}$/, message: '手機號碼格式不正確', trigger: ['blur', 'input'] }
      ]
      baseRules.role = [{ required: true, message: '角色為必填', trigger: ['change'] }]

      if (props.mode === 'add') {
        baseRules.password = [
          {
            required: false,
            trigger: ['blur', 'input'],
            validator: (rule, value) => {
              if (value && value.length < 6) return new Error('密碼長度至少需要6位')
              return true
            }
          }
        ]
      }
    }

    return baseRules
  })

  // Watch role changes for guest handling
  watch(
    () => formData.role,
    newRole => {
      if (newRole === 'guest') {
        // 清空帳號相關欄位
        formData.username = ''
        formData.password = ''
        formData.email = ''
      }
    }
  )

  // Methods
  const goBack = () => {
    router.push({ name: 'ManagementCenter' })
  }

  const populateForm = data => {
    if (!data) return

    formData.id = data.id
    formData.name = data.name || ''
    formData.student_id = data.student_id || ''
    formData.gender = isValidOption(genderOptions, data.gender) ? data.gender : null
    formData.position = isValidOption(positionOptions, data.position) ? data.position : null
    formData.organization_id = data.organization_id || null
    formData.mu = data.mu
    formData.sigma = data.sigma
    formData.notes = data.notes || ''
    formData.joined_date_ts = data.joined_date ? new Date(data.joined_date).getTime() : null
    formData.leaved_date_ts = data.leaved_date ? new Date(data.leaved_date).getTime() : null

    if (data.user) {
      formData.username = data.user.username || ''
      formData.email = data.user.email || ''
      formData.display_name = data.user.display_name || ''
      formData.role = data.user.role || 'member'
      formData.is_active = data.user.is_active ?? true
    } else {
      formData.username = ''
      formData.email = ''
      formData.display_name = ''
      formData.role = 'guest' // 沒有 user 的話預設為訪客
      formData.is_active = false
    }
  }

  const fetchMemberData = async () => {
    if (props.mode !== 'edit' || !props.id) return

    isLoading.value = true
    fetchError.value = null

    try {
      const response = await fetchData(`/members/${props.id}`, {
        showLoading: false,
        showError: false
      })
      populateForm(response.data)
    } catch (err) {
      fetchError.value = err.response?.data?.message || '無法載入成員資料'
    } finally {
      isLoading.value = false
    }
  }

  const formatDate = timestamp => {
    if (!timestamp) return null
    const date = new Date(timestamp)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const handleSubmit = () => {
    formRef.value?.validate(async validationErrors => {
      if (validationErrors) {
        message.error('請檢查表單，修正錯誤後再提交')
        return
      }

      try {
        if (props.mode === 'add') {
          await createMember(formData, {
            onSuccess: () => {
              message.success('成員新增成功！')
              goBack()
            },
            onError: err => {
              const errorData = err.response?.data
              if (errorData?.details) {
                submitMessage.value =
                  '新增失敗，請檢查以下欄位：\n' + Object.values(errorData.details).flat().join('\n')
              } else {
                submitMessage.value = errorData?.message || '新增成員時發生未預期錯誤'
              }
              submitStatus.value = 'error'
            }
          })
        } else {
          // 編輯模式：包含離隊日期
          const memberData = {
            ...formData,
            leaved_date_ts: formData.leaved_date_ts // 加入離隊日期
          }

          await updateMember(props.id, memberData, {
            onSuccess: () => {
              message.success('成員資料更新成功！')
              goBack()
            },
            onError: err => {
              submitMessage.value = err.response?.data?.message || '更新失敗，請稍後再試'
              submitStatus.value = 'error'
            }
          })
        }
      } catch (error) {
        console.error('❌ 意外錯誤:', error)
        submitMessage.value = '發生未預期的錯誤，請稍後再試'
        submitStatus.value = 'error'
      }
    })
  }

  const clearSubmitMessage = () => {
    submitMessage.value = ''
    submitStatus.value = ''
  }

  const resetForm = () => {
    Object.assign(formData, {
      id: null,
      name: '',
      display_name: '',
      username: '',
      password: '',
      email: '',
      role: 'member',
      student_id: '',
      gender: null,
      position: null,
      organization_id: null,
      is_active: true,
      joined_date_ts: null,
      leaved_date_ts: null,
      notes: '',
      mu: null,
      sigma: null
    })
  }

  // Lifecycle
  onMounted(async () => {
    isLoading.value = true

    try {
      await loadOrganizationOptions()
      if (props.mode === 'edit') {
        await fetchMemberData()
      }
    } catch (error) {
      console.error('初始化失敗:', error)
    } finally {
      isLoading.value = false
    }
  })
</script>

<style scoped>
  .member-form-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 2rem 1rem;
  }

  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
  }

  .error-alert {
    max-width: 800px;
    margin: 0 auto 2rem auto;
  }

  .form-container {
    max-width: 900px;
    margin: 0 auto;
  }

  /* 現代化頁面標題 */
  .page-header {
    margin-bottom: 2rem;
  }

  .header-content {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
  }

  .back-button {
    padding: 0.75rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    margin-top: 0.25rem;
  }

  .back-button:hover {
    background: rgba(255, 255, 255, 1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  .title-section {
    flex: 1;
  }

  .page-title {
    font-size: 2.25rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .guest-tag {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    border: none;
    color: #8b4513;
    font-weight: 600;
  }

  .page-subtitle {
    font-size: 1.1rem;
    color: #64748b;
    margin: 0;
    font-weight: 400;
  }

  /* 現代化表單卡片 */
  .form-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 2.5rem;
  }

  /* 表單區塊樣式 */
  .form-section {
    margin-bottom: 3rem;
  }

  .form-section:last-of-type {
    margin-bottom: 2rem;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
  }

  .section-icon {
    font-size: 1.5rem;
    color: #667eea;
  }

  .section-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    color: #334155;
  }

  .section-description {
    margin-left: auto;
    font-size: 0.9rem;
    font-style: italic;
  }

  /* 狀態切換器 */
  .status-toggle {
    display: flex;
    align-items: center;
    height: 40px;
  }

  /* 動作區塊 */
  .action-section {
    padding-top: 2rem;
    border-top: 1px solid rgba(226, 232, 240, 0.8);
  }

  .submit-alert {
    margin-bottom: 1.5rem;
  }

  /* 響應式設計 */
  @media (max-width: 768px) {
    .member-form-page {
      padding: 1rem 0.5rem;
    }

    .form-card {
      padding: 1.5rem;
      border-radius: 16px;
    }

    .page-title {
      font-size: 1.75rem;
    }

    .header-content {
      flex-direction: column;
      gap: 0.5rem;
    }

    .back-button {
      align-self: flex-start;
    }
  }

  /* Nintendo 風格的按鈕增強 */
  :deep(.n-button--primary) {
    background: linear-gradient(135deg, #e60012 0%, #ff6b6b 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
    transition: all 0.3s ease;
  }

  :deep(.n-button--primary:hover) {
    background: linear-gradient(135deg, #cc0010 0%, #ff5252 100%);
    box-shadow: 0 6px 20px rgba(230, 0, 18, 0.4);
    transform: translateY(-2px);
  }

  /* 表單控件增強 */
  :deep(.n-input),
  :deep(.n-select),
  :deep(.n-date-picker) {
    border-radius: 12px;
  }

  :deep(.n-input--focus),
  :deep(.n-select--focus) {
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
</style>
