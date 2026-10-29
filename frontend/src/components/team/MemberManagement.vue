<template>
  <div class="member-management">
    <!-- 現代化操作頭部 -->
    <div class="management-header">
      <div class="header-info">
        <h3 class="section-title">
          <n-icon :component="PeopleIcon" class="title-icon" />
          成員管理
        </h3>
      </div>

      <!--      <div class="header-actions">-->
      <!--        <n-button-->
      <!--          v-if="canEditMember"-->
      <!--          type="primary"-->
      <!--          size="medium"-->
      <!--          @click="goToAddMember"-->
      <!--          class="add-btn"-->
      <!--        >-->
      <!--          <template #icon>-->
      <!--            <n-icon :component="PersonAddIcon" />-->
      <!--          </template>-->
      <!--          新增成員-->
      <!--        </n-button>-->
      <!--      </div>-->
    </div>

    <!-- 錯誤提示 -->
    <n-alert v-if="memberError" title="載入錯誤" type="error" closable class="error-alert" @close="memberError = null">
      {{ memberError }}
    </n-alert>

    <!-- 現代化表格 -->
    <div class="table-container">
      <n-data-table
        :columns="memberTableColumns"
        :data="paginatedMembers"
        :loading="loadingMembers"
        :pagination="paginationConfig"
        :bordered="false"
        :single-line="false"
        size="medium"
        striped
        :scroll-x="1000"
        class="modern-table"
        flex-height
        style="height: 600px"
      />
    </div>

    <!-- 空狀態 -->
    <div v-if="!loadingMembers && filteredMembers.length === 0" class="empty-container">
      <n-empty
        :description="searchTermProp ? `找不到符合 '${searchTermProp}' 的成員` : '還沒有成員資料'"
        class="empty-state"
      >
        <template #extra>
          <n-button v-if="canEditMember && !searchTermProp" type="primary" @click="goToAddMember">
            新增第一位成員
          </n-button>
        </template>
      </n-empty>
    </div>
  </div>
</template>

<script setup>
  import { computed, h, onMounted, reactive, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { NAlert, NButton, NDataTable, NEmpty, NIcon, NSpace, NTag, NTooltip, useDialog, useMessage } from 'naive-ui'
  import {
    PencilOutline as EditIcon,
    PersonAddOutline as PersonAddIcon,
    TrashBinOutline as DeleteIcon,
    PeopleOutline as PeopleIcon,
    PersonOutline as GuestIcon,
    ShieldOutline as AdminIcon,
    PeopleOutline as CadreIcon,
    SchoolOutline as CoachIcon,
    PersonCircleOutline as MemberIcon
  } from '@vicons/ionicons5'
  import apiClient from '@/services/apiClient'
  import { useOptions } from '@/composables/useOptions'
  import { usePermissions } from '@/composables/usePermissions'

  // Props
  const props = defineProps({
    searchTermProp: { type: String, default: '' },
    showGuestLabels: { type: Boolean, default: true }
  })

  // Emits - 關鍵：統計數據事件
  const emit = defineEmits(['member-count-update', 'guest-count-update'])

  // Composables
  const router = useRouter()
  const dialog = useDialog()
  const message = useMessage()
  const { getRoleDisplay, getRoleColor, isGuest, getGenderDisplay, getPositionDisplay } = useOptions()
  const { canEditMember } = usePermissions()

  // 圖標映射
  const roleIconMap = {
    admin: AdminIcon,
    coach: CoachIcon,
    cadre: CadreIcon,
    member: MemberIcon,
    guest: GuestIcon
  }

  // State
  const allFetchedMembers = ref([])
  const loadingMembers = ref(true)
  const memberError = ref(null)
  const currentPage = ref(1)
  const pageSize = ref(15)

  // 分頁配置
  const memberPagination = reactive({
    page: 1,
    pageSize: 15,
    showSizePicker: true,
    pageSizes: [10, 15, 20, 30, 50],
    onChange: page => {
      currentPage.value = page
      memberPagination.page = page
    },
    onUpdatePageSize: newPageSize => {
      pageSize.value = newPageSize
      memberPagination.pageSize = newPageSize
      currentPage.value = 1
      memberPagination.page = 1
    }
  })

  // Computed
  const memberCount = computed(() => allFetchedMembers.value.length)

  const guestCount = computed(() => {
    return allFetchedMembers.value.filter(member => isGuest(member.user?.role) || member.is_guest).length
  })

  const filteredMembers = computed(() => {
    if (!props.searchTermProp) return allFetchedMembers.value

    const term = props.searchTermProp.toLowerCase().trim()
    return allFetchedMembers.value.filter(member => {
      const searchFields = [
        member.name,
        member.display_name,
        member.user?.display_name,
        member.student_id,
        member.organization?.name,
        member.organization?.short_name,
        member.user?.username,
        getRoleDisplay(member.user?.role)
      ]

      return searchFields.some(field => field && String(field).toLowerCase().includes(term))
    })
  })

  const paginatedMembers = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return filteredMembers.value.slice(start, end)
  })

  const paginationConfig = computed(() => ({
    ...memberPagination,
    page: currentPage.value,
    pageSize: pageSize.value,
    itemCount: filteredMembers.value.length,
    prefix: ({ itemCount }) => `共 ${itemCount} 位成員`
  }))

  // 表格列定義 - 按照需求順序：name, display name, role, student id, gender, position, org, 操作
  const memberTableColumns = computed(() => [
    {
      title: '姓名',
      key: 'name',
      sorter: 'default',
      width: 140,
      fixed: 'left',
      ellipsis: { tooltip: true },
      render: row => {
        const isGuestUser = isGuest(row.user?.role) || row.is_guest

        return h('div', { class: 'name-cell' }, [
          h('div', { class: 'name-main' }, [
            h(
              'span',
              {
                class: 'member-name',
                onClick: () => editMember(row.id),
                style: { cursor: 'pointer' }
              },
              row.name
            ),
            // 訪客指示器
            isGuestUser && props.showGuestLabels
              ? h('span', {
                  class: 'guest-indicator',
                  title: '訪客用戶'
                })
              : null
          ])
        ])
      }
    },
    {
      title: '顯示名稱',
      key: 'display_name',
      width: 120,
      ellipsis: { tooltip: true },
      render: row => {
        const displayName = row.display_name || row.user?.display_name
        return displayName ? h('span', { class: 'display-name' }, displayName) : h('span', { class: 'text-muted' }, '-')
      }
    },
    {
      title: '角色',
      key: 'role',
      width: 100,
      align: 'center',
      filterOptions: [
        { label: '管理員', value: 'admin' },
        { label: '幹部', value: 'cadre' },
        { label: '教練', value: 'coach' },
        { label: '隊員', value: 'member' },
        { label: '訪客', value: 'guest' }
      ],
      filter: (value, row) => (row.user?.role || (row.is_guest ? 'guest' : 'member')) === value,
      render: row => {
        let role = row.user?.role

        // 如果沒有user或role，但is_guest為true，則視為訪客
        if (!role && row.is_guest) {
          role = 'guest'
        } else if (!role) {
          role = 'member'
        }

        const IconComponent = roleIconMap[role] || MemberIcon

        return h(
          NTag,
          {
            type: getRoleColor(role),
            round: true,
            size: 'small',
            class: isGuest(role) || row.is_guest ? 'guest-tag' : ''
          },
          {
            icon: () => h(NIcon, { component: IconComponent, size: 14 }),
            default: () => getRoleDisplay(role)
          }
        )
      }
    },
    {
      title: '學號',
      key: 'student_id',
      sorter: 'default',
      width: 110,
      render: row => row.student_id || '-'
    },
    {
      title: '性別',
      key: 'gender',
      width: 70,
      align: 'center',
      filterOptions: [
        { label: '男', value: 'male' },
        { label: '女', value: 'female' }
      ],
      filter: (value, row) => row.gender === value,
      render: row => getGenderDisplay(row.gender) || '-'
    },
    {
      title: '位置',
      key: 'position',
      width: 80,
      align: 'center',
      filterOptions: [
        { label: '後排', value: 'back' },
        { label: '前排', value: 'front' },
        { label: '皆可', value: 'versatile' }
      ],
      filter: (value, row) => row.position === value,
      render: row => getPositionDisplay(row.position) || '-'
    },
    {
      title: '組織',
      key: 'organization_name',
      sorter: 'default',
      width: 150,
      ellipsis: { tooltip: true },
      render: row => row.organization?.short_name || row.organization?.name || '-'
    },
    {
      title: '操作',
      key: 'actions',
      fixed: 'right',
      width: 100,
      align: 'center',
      render: row => {
        const isGuestUser = isGuest(row.user?.role) || row.is_guest

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
                    onClick: () => editMember(row.id)
                  },
                  {
                    icon: () => h(NIcon, { component: EditIcon, size: 16 })
                  }
                ),
              default: () => (isGuestUser ? '編輯訪客' : '編輯成員')
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
                    onClick: () => confirmDeleteMember(row)
                  },
                  {
                    icon: () => h(NIcon, { component: DeleteIcon, size: 16 })
                  }
                ),
              default: () => '刪除'
            }
          )
        ])
      }
    }
  ])

  // Methods
  const fetchMembers = async () => {
    loadingMembers.value = true
    memberError.value = null

    try {
      const response = await apiClient.get('/members', { params: { include_inactive: true, include_guests: true } })
      allFetchedMembers.value = response.data || []
      console.log('✅ 載入成員數據:', allFetchedMembers.value.length)

      // 發送統計數據到父組件
      emit('member-count-update', memberCount.value)
      emit('guest-count-update', guestCount.value)
    } catch (err) {
      memberError.value = err.response?.data?.message || '無法載入成員列表'
      console.error('❌ 載入成員失敗:', err)
    } finally {
      loadingMembers.value = false
    }
  }

  const goToAddMember = () => {
    router.push({ name: 'AddMember' })
  }

  const editMember = memberId => {
    router.push({ name: 'EditMember', params: { id: memberId } })
  }

  const confirmDeleteMember = member => {
    const memberType = isGuest(member.user?.role) || member.is_guest ? '訪客' : '成員'

    dialog.error({
      title: '確認刪除',
      content: `您確定要刪除${memberType} "${member.name}" 嗎？此操作將一併刪除其關聯的登入帳號，且無法復原！`,
      positiveText: '確認刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await apiClient.delete(`/members/${member.id}`)
          message.success(`${memberType} ${member.name} 已成功刪除`)
          await fetchMembers()
        } catch (err) {
          message.error(err.response?.data?.message || '刪除失敗')
        }
      }
    })
  }

  // Watchers
  watch(
    [memberCount, guestCount],
    ([newMemberCount, newGuestCount]) => {
      console.log('📊 統計數據變化:', { members: newMemberCount, guests: newGuestCount })
      emit('member-count-update', newMemberCount)
      emit('guest-count-update', newGuestCount)
    },
    { immediate: true }
  )

  watch(
    () => props.searchTermProp,
    () => {
      currentPage.value = 1
      memberPagination.page = 1
    }
  )

  // Lifecycle
  onMounted(() => {
    fetchMembers()
  })
</script>

<style scoped>
  .member-management {
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
    color: #667eea;
  }

  .header-actions {
    display: flex;
    gap: 1rem;
  }

  .add-btn {
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    background: linear-gradient(135deg, #e60012 0%, #ff6b6b 100%);
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
  }

  .add-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(230, 0, 18, 0.4);
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

  /* 姓名單元格 */
  .name-cell {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .name-main {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .member-name {
    font-weight: 600;
    color: #1a202c;
    transition: color 0.2s ease;
  }

  .member-name:hover {
    color: #e60012;
    text-decoration: underline;
  }

  .display-name {
    color: #64748b;
    font-weight: 500;
  }

  .text-muted {
    color: #9ca3af;
    font-style: italic;
  }

  /* 訪客指示器 */
  .guest-indicator {
    width: 8px;
    height: 8px;
    background: linear-gradient(135deg, #ff8c42 0%, #ff6b42 100%);
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
    position: relative;
  }

  .guest-indicator::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    width: 12px;
    height: 12px;
    background: rgba(255, 140, 66, 0.3);
    border-radius: 50%;
    animation: ripple 2s infinite;
  }

  /* 訪客標籤 */
  :deep(.guest-tag) {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%) !important;
    color: #8b4513 !important;
    border: 1px solid rgba(252, 182, 159, 0.3) !important;
    font-weight: 600;
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
    font-size: 0.875rem;
  }

  :deep(.modern-table .n-data-table-td) {
    transition: background-color 0.2s ease;
    font-size: 0.875rem;
  }

  :deep(.modern-table .n-data-table-tr:hover) {
    background: linear-gradient(135deg, rgba(230, 0, 18, 0.02) 0%, rgba(255, 107, 107, 0.02) 100%);
  }

  /* 動畫 */
  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  @keyframes ripple {
    0% {
      transform: scale(0.8);
      opacity: 1;
    }
    100% {
      transform: scale(2);
      opacity: 0;
    }
  }

  /* 響應式設計 */
  @media (max-width: 1200px) {
    .table-container {
      padding: 1rem;
    }

    /* 在小螢幕上隱藏一些欄位 */
    :deep(.modern-table .n-data-table-th:nth-child(2)),
    :deep(.modern-table .n-data-table-td:nth-child(2)) {
      display: none; /* 隱藏顯示名稱欄 */
    }
  }

  @media (max-width: 768px) {
    .management-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .header-info {
      justify-content: space-between;
    }

    /* 在更小螢幕上隱藏更多欄位 */
    :deep(.modern-table .n-data-table-th:nth-child(5)),
    :deep(.modern-table .n-data-table-td:nth-child(5)),
    :deep(.modern-table .n-data-table-th:nth-child(6)),
    :deep(.modern-table .n-data-table-td:nth-child(6)) {
      display: none; /* 隱藏性別和位置欄 */
    }
  }

  @media (max-width: 480px) {
    /* 在最小螢幕上隱藏組織欄 */
    :deep(.modern-table .n-data-table-th:nth-child(7)),
    :deep(.modern-table .n-data-table-td:nth-child(7)) {
      display: none; /* 隱藏組織欄 */
    }
  }
</style>
