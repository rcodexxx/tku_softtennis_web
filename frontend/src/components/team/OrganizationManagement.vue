<template>
  <div class="organization-management">
    <!-- 現代化操作頭部 -->
    <div class="management-header">
      <div class="header-info">
        <h3 class="section-title">
          <n-icon :component="BuildingIcon" class="title-icon" />
          組織管理
        </h3>
      </div>

      <!--      <div class="header-actions">-->
      <!--        <n-button-->
      <!--          v-if="canManageOrganization"-->
      <!--          type="primary"-->
      <!--          size="medium"-->
      <!--          @click="openFormModal(null)"-->
      <!--          class="add-btn"-->
      <!--        >-->
      <!--          <template #icon>-->
      <!--            <n-icon :component="BuildingAddIcon" />-->
      <!--          </template>-->
      <!--          新增組織-->
      <!--        </n-button>-->
      <!--      </div>-->
    </div>

    <!-- 錯誤提示 -->
    <n-alert v-if="fetchError" title="載入錯誤" type="error" closable class="error-alert" @close="fetchError = null">
      {{ fetchError }}
    </n-alert>

    <!-- 現代化表格 -->
    <div class="table-container">
      <n-data-table
        :columns="tableColumns"
        :data="filteredOrganizations"
        :loading="loading"
        :pagination="paginationConfig"
        :bordered="false"
        :single-line="false"
        size="medium"
        striped
        :scroll-x="800"
        class="modern-table"
      />
    </div>

    <!-- 空狀態 -->
    <div v-if="!loading && filteredOrganizations.length === 0" class="empty-container">
      <n-empty
        :description="searchTermProp ? `找不到符合 '${searchTermProp}' 的組織` : '還沒有組織資料'"
        class="empty-state"
      >
        <template #extra>
          <n-button v-if="canManageOrganization && !searchTermProp" type="primary" @click="openFormModal(null)">
            新增第一個組織
          </n-button>
        </template>
      </n-empty>
    </div>

    <!-- 現代化新增/編輯表單模態框 -->
    <n-modal
      v-model:show="showFormModal"
      :mask-closable="false"
      preset="card"
      :title="isEditing ? '編輯組織' : '新增組織'"
      class="form-modal"
      :bordered="false"
    >
      <n-form
        ref="formRef"
        :model="currentOrg"
        :rules="formRules"
        label-placement="top"
        class="org-form"
        @submit.prevent="handleFormSubmit"
      >
        <div class="form-section">
          <h4 class="form-section-title">
            <n-icon :component="InfoIcon" class="section-icon" />
            基本資訊
          </h4>

          <n-grid :x-gap="24" :y-gap="16" :cols="2">
            <n-form-item-gi :span="1" label="組織全名" path="name">
              <n-input v-model:value="currentOrg.name" placeholder="請輸入組織全名" size="large" />
            </n-form-item-gi>
            <n-form-item-gi :span="1" label="組織簡稱" path="short_name">
              <n-input v-model:value="currentOrg.short_name" placeholder="例如：淡大軟網" size="large" />
            </n-form-item-gi>
          </n-grid>

          <n-form-item label="組織描述" path="description">
            <n-input
              v-model:value="currentOrg.description"
              type="textarea"
              placeholder="關於組織的簡介（選填）"
              :autosize="{ minRows: 3, maxRows: 6 }"
              size="large"
            />
          </n-form-item>
        </div>

        <div class="form-section">
          <h4 class="form-section-title">
            <n-icon :component="ContactIcon" class="section-icon" />
            聯絡資訊
          </h4>

          <n-grid :x-gap="24" :y-gap="16" :cols="2">
            <n-form-item-gi :span="1" label="主要聯絡人" path="contact_person">
              <n-input v-model:value="currentOrg.contact_person" placeholder="聯絡人姓名（選填）" size="large" />
            </n-form-item-gi>
            <n-form-item-gi :span="1" label="聯絡電話" path="contact_phone">
              <n-input v-model:value="currentOrg.contact_phone" placeholder="電話號碼（選填）" size="large" />
            </n-form-item-gi>
          </n-grid>

          <n-form-item label="聯絡Email" path="contact_email">
            <n-input v-model:value="currentOrg.contact_email" placeholder="email@example.com（選填）" size="large" />
          </n-form-item>
        </div>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-space justify="end" :size="16">
            <n-button size="large" @click="showFormModal = false"> 取消 </n-button>
            <n-button type="primary" size="large" :loading="submitting" strong @click="handleFormSubmit">
              <template #icon>
                <n-icon :component="isEditing ? SaveIcon : AddIcon" />
              </template>
              {{ isEditing ? '確認更新' : '確認新增' }}
            </n-button>
          </n-space>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, h, onMounted, reactive, ref, watch } from 'vue'
  import {
    NAlert,
    NButton,
    NDataTable,
    NEmpty,
    NForm,
    NFormItem,
    NFormItemGi,
    NGi,
    NGrid,
    NIcon,
    NInput,
    NModal,
    NSpace,
    NTag,
    NTooltip,
    useDialog,
    useMessage
  } from 'naive-ui'
  import {
    AddCircleOutline as BuildingAddIcon,
    PencilOutline as EditIcon,
    TrashBinOutline as DeleteIcon,
    BusinessOutline as BuildingIcon,
    InformationCircleOutline as InfoIcon,
    CallOutline as ContactIcon,
    SaveOutline as SaveIcon,
    AddOutline as AddIcon
  } from '@vicons/ionicons5'
  import apiClient from '@/services/apiClient'
  import { usePermissions } from '@/composables/usePermissions'

  // Props
  const props = defineProps({
    searchTermProp: { type: String, default: '' }
  })

  // Emits - 關鍵：統計數據事件
  const emit = defineEmits(['organization-count-update'])

  // Composables
  const dialog = useDialog()
  const message = useMessage()
  const { canManageOrganization } = usePermissions()

  // State
  const allOrganizations = ref([])
  const loading = ref(true)
  const fetchError = ref(null)

  // Modal 相關狀態
  const showFormModal = ref(false)
  const isEditing = ref(false)
  const submitting = ref(false)
  const formRef = ref(null)
  const currentOrg = reactive({
    id: null,
    name: '',
    short_name: '',
    description: '',
    contact_person: '',
    contact_email: '',
    contact_phone: ''
  })

  // 分頁配置
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    showSizePicker: true,
    pageSizes: [10, 20, 30, 50]
  })

  // 表單驗證規則
  const formRules = {
    name: [{ required: true, message: '組織全名為必填', trigger: ['input', 'blur'] }],
    contact_email: [{ type: 'email', message: '請輸入有效的電子郵件格式', trigger: ['blur'] }]
  }

  // Computed
  const organizationCount = computed(() => allOrganizations.value.length)

  const filteredOrganizations = computed(() => {
    if (!props.searchTermProp) return allOrganizations.value

    const term = props.searchTermProp.toLowerCase().trim()
    return allOrganizations.value.filter(
      org =>
        (org.name && org.name.toLowerCase().includes(term)) ||
        (org.short_name && org.short_name.toLowerCase().includes(term)) ||
        (org.contact_person && org.contact_person.toLowerCase().includes(term))
    )
  })

  const paginationConfig = computed(() => ({
    ...pagination,
    itemCount: filteredOrganizations.value.length,
    prefix: ({ itemCount }) => `共 ${itemCount} 個組織`
  }))

  // 表格列定義
  const tableColumns = computed(() => [
    {
      title: '組織名稱',
      key: 'name',
      sorter: 'default',
      width: 200,
      fixed: 'left',
      ellipsis: { tooltip: true },
      render: row => {
        return h('div', { class: 'org-name-cell' }, [
          h(
            'div',
            {
              class: 'org-name',
              onClick: () => openFormModal(row),
              style: { cursor: 'pointer' }
            },
            row.name
          ),
          row.short_name ? h('div', { class: 'org-short-name' }, `(${row.short_name})`) : null
        ])
      }
    },
    {
      title: '聯絡人',
      key: 'contact_person',
      sorter: 'default',
      width: 120,
      render: row => row.contact_person || '-'
    },
    {
      title: '聯絡方式',
      key: 'contact_info',
      width: 180,
      render: row => {
        const contacts = []
        if (row.contact_phone) contacts.push(`📞 ${row.contact_phone}`)
        if (row.contact_email) contacts.push(`📧 ${row.contact_email}`)
        return contacts.length > 0 ? contacts.join(' | ') : '-'
      }
    },
    {
      title: '成員數',
      key: 'members_count',
      sorter: (a, b) => (a.members_count || 0) - (b.members_count || 0),
      width: 100,
      align: 'right',
      render: row => {
        const count = row.members_count || 0
        return h(
          NTag,
          {
            type: count > 0 ? 'info' : 'default',
            size: 'small',
            round: true
          },
          {
            default: () => `${count} 人`
          }
        )
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      align: 'center',
      fixed: 'right',
      render: row => {
        return h(NSpace, { justify: 'center', size: 8 }, () => [
          h(
            NTooltip,
            {},
            {
              trigger: () =>
                h(
                  NButton,
                  {
                    size: 'small',
                    type: 'primary',
                    ghost: true,
                    onClick: () => openFormModal(row)
                  },
                  {
                    icon: () => h(NIcon, { component: EditIcon, size: 16 })
                  }
                ),
              default: () => '編輯'
            }
          ),

          h(
            NTooltip,
            {},
            {
              trigger: () =>
                h(
                  NButton,
                  {
                    size: 'small',
                    type: 'error',
                    ghost: true,
                    disabled: (row.members_count || 0) > 0,
                    onClick: () => confirmDelete(row)
                  },
                  {
                    icon: () => h(NIcon, { component: DeleteIcon, size: 16 })
                  }
                ),
              default: () =>
                (row.members_count || 0) > 0 ? `組織尚有 ${row.members_count} 位成員，無法刪除` : '刪除組織'
            }
          )
        ])
      }
    }
  ])

  // Methods
  const fetchOrganizations = async () => {
    loading.value = true
    fetchError.value = null

    try {
      const response = await apiClient.get('/organizations')
      allOrganizations.value = response.data || []
      console.log('✅ 載入組織數據:', allOrganizations.value.length)

      // 發送統計數據到父組件
      emit('organization-count-update', organizationCount.value)
    } catch (err) {
      fetchError.value = err.response?.data?.message || '無法載入組織列表'
      console.error('❌ 載入組織失敗:', err)
    } finally {
      loading.value = false
    }
  }

  const openFormModal = (org = null) => {
    formRef.value?.restoreValidation()

    if (org) {
      isEditing.value = true
      Object.assign(currentOrg, org)
    } else {
      isEditing.value = false
      Object.assign(currentOrg, {
        id: null,
        name: '',
        short_name: '',
        description: '',
        contact_person: '',
        contact_email: '',
        contact_phone: ''
      })
    }

    showFormModal.value = true
  }

  const handleFormSubmit = async () => {
    if (!formRef.value) return

    formRef.value.validate(async errors => {
      if (errors) {
        message.error('請檢查表單輸入')
        return
      }

      submitting.value = true

      try {
        const payload = {
          name: currentOrg.name.trim(),
          short_name: currentOrg.short_name?.trim() || null,
          description: currentOrg.description?.trim() || null,
          contact_person: currentOrg.contact_person?.trim() || null,
          contact_email: currentOrg.contact_email?.trim() || null,
          contact_phone: currentOrg.contact_phone?.trim() || null
        }

        if (isEditing.value) {
          await apiClient.put(`/organizations/${currentOrg.id}`, payload)
          message.success('組織已成功更新！')
        } else {
          await apiClient.post('/organizations', payload)
          message.success('組織已成功新增！')
        }

        showFormModal.value = false
        await fetchOrganizations()
      } catch (err) {
        message.error(err.response?.data?.message || '操作失敗')
      } finally {
        submitting.value = false
      }
    })
  }

  const confirmDelete = org => {
    dialog.error({
      title: '確認刪除組織',
      content: `您確定要刪除組織 "${org.name}" 嗎？此操作無法復原！`,
      positiveText: '確認刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await apiClient.delete(`/organizations/${org.id}`)
          message.success(`組織 "${org.name}" 已成功刪除`)
          await fetchOrganizations()
        } catch (err) {
          message.error(err.response?.data?.message || '刪除組織失敗')
        }
      }
    })
  }

  // Watchers
  watch(
    organizationCount,
    newCount => {
      console.log('📊 組織數量變化:', newCount)
      emit('organization-count-update', newCount)
    },
    { immediate: true }
  )

  watch(
    () => props.searchTermProp,
    () => {
      pagination.page = 1
    }
  )

  // Lifecycle
  onMounted(() => {
    fetchOrganizations()
  })

  defineExpose({
    openFormModal,
    fetchOrganizations
  })
</script>

<style scoped>
  .organization-management {
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  /* 現代化頭部 */
  .management-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .header-info {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #334155;
  }

  .title-icon {
    font-size: 1.5rem;
    color: #f093fb;
  }

  .stats-mini {
    display: flex;
    gap: 0.75rem;
  }

  .header-actions {
    display: flex;
    gap: 1rem;
  }

  .add-btn {
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
  }

  .add-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(240, 147, 251, 0.4);
  }

  /* 錯誤提示 */
  .error-alert {
    border-radius: 12px;
  }

  /* 表格容器 */
  .table-container {
    flex: 1;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .modern-table {
    border-radius: 12px;
    overflow: hidden;
  }

  /* 組織名稱單元格 */
  .org-name-cell {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .org-name {
    font-weight: 600;
    color: #1a202c;
    transition: color 0.2s ease;
  }

  .org-name:hover {
    color: #f093fb;
    text-decoration: underline;
  }

  .org-short-name {
    font-size: 0.75rem;
    color: #64748b;
    font-style: italic;
  }

  /* 空狀態 */
  .empty-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 300px;
  }

  .empty-state {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 3rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  /* 表單模態框 */
  .form-modal {
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    max-width: 700px;
    width: 90vw;
  }

  .org-form {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 1rem;
  }

  .form-section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: rgba(248, 250, 252, 0.5);
    border-radius: 12px;
    border: 1px solid rgba(226, 232, 240, 0.6);
  }

  .form-section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
  }

  .section-icon {
    font-size: 1.25rem;
    color: #667eea;
  }

  .modal-footer {
    padding-top: 1rem;
    border-top: 1px solid rgba(226, 232, 240, 0.6);
  }

  /* 表格增強 */
  :deep(.modern-table .n-data-table) {
    background: transparent;
  }

  :deep(.modern-table .n-data-table-thead) {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  }

  :deep(.modern-table .n-data-table-th) {
    font-weight: 700;
    color: #374151;
    border-bottom: 2px solid #e5e7eb;
    background: transparent;
  }

  :deep(.modern-table .n-data-table-td) {
    transition: background-color 0.2s ease;
  }

  :deep(.modern-table .n-data-table-tr:hover) {
    background: linear-gradient(135deg, rgba(240, 147, 251, 0.02) 0%, rgba(245, 87, 108, 0.02) 100%);
  }

  /* 響應式設計 */
  @media (max-width: 768px) {
    .management-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .header-info {
      justify-content: space-between;
    }

    .stats-mini {
      justify-content: center;
    }

    .table-container {
      padding: 1rem;
    }

    .form-modal {
      width: 95vw;
      max-width: none;
    }

    .org-form {
      padding-right: 0;
    }
  }
</style>
