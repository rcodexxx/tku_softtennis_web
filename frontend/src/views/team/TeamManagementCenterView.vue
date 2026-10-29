<template>
  <div class="management-center-page">
    <!-- 1. 標題 + 統計卡片 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">團隊管理中心</h1>
        </div>

        <!-- 快速統計卡片 -->
        <div class="stats-cards">
          <div class="stat-card members-stat">
            <div class="stat-icon">
              <n-icon :component="PeopleIcon" size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ memberCount }}</span>
              <span class="stat-label">成員</span>
            </div>
            <div v-if="loadingStats" class="stat-loading">
              <n-spin size="small" />
            </div>
          </div>

          <div class="stat-card organizations-stat">
            <div class="stat-icon">
              <n-icon :component="BuildingIcon" size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ organizationCount }}</span>
              <span class="stat-label">組織</span>
            </div>
            <div v-if="loadingStats" class="stat-loading">
              <n-spin size="small" />
            </div>
          </div>

          <div class="stat-card guests-stat">
            <div class="stat-icon">
              <n-icon :component="PersonIcon" size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ guestCount }}</span>
              <span class="stat-label">訪客</span>
            </div>
            <div v-if="loadingStats" class="stat-loading">
              <n-spin size="small" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 搜尋區域 -->
    <div class="search-section">
      <div class="search-container">
        <n-input
          v-model:value="searchTerm"
          :placeholder="searchPlaceholder"
          clearable
          size="large"
          class="modern-search"
        >
          <template #prefix>
            <n-icon :component="SearchIcon" />
          </template>
          <template #suffix>
            <n-button v-if="searchTerm" text size="small" class="clear-search-btn" @click="clearSearch">
              <n-icon :component="CloseIcon" size="16" />
            </n-button>
          </template>
        </n-input>

        <!-- 刷新統計按鈕 -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="large" :loading="loadingStats" class="refresh-btn" @click="refreshStats">
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
            </n-button>
          </template>
          重新載入統計數據
        </n-tooltip>
      </div>
    </div>

    <!-- 3. 選項 + 組件內容 -->
    <div class="main-content-section">
      <!-- 導航標籤 + 操作按鈕 -->
      <div class="content-header">
        <n-tabs v-model:value="currentView" type="card" animated class="content-tabs" @update:value="handleTabChange">
          <n-tab-pane name="members" tab="成員管理">
            <template #tab>
              <div class="tab-content">
                <n-icon :component="PeopleIcon" size="18" class="tab-icon" />
                <span class="tab-text">成員管理</span>
              </div>
            </template>
          </n-tab-pane>

          <n-tab-pane name="organizations" tab="組織管理">
            <template #tab>
              <div class="tab-content">
                <n-icon :component="BuildingIcon" size="18" class="tab-icon" />
                <span class="tab-text">組織管理</span>
              </div>
            </template>
          </n-tab-pane>
        </n-tabs>

        <!-- 操作按鈕區域 -->
        <div class="header-actions">
          <n-button
            v-if="currentView === 'members' && canEditMember"
            type="primary"
            size="medium"
            class="action-btn"
            @click="goToAddMember"
          >
            <template #icon>
              <n-icon :component="AddIcon" />
            </template>
            新增成員
          </n-button>

          <n-button
            v-if="currentView === 'organizations' && canEditMember"
            type="primary"
            size="medium"
            class="action-btn"
            @click="goToAddOrganization"
          >
            <template #icon>
              <n-icon :component="AddIcon" />
            </template>
            新增組織
          </n-button>
        </div>
      </div>

      <!-- 組件內容區域 -->
      <div class="content-body">
        <transition name="content-fade" mode="out-in">
          <div v-if="currentView === 'members'" key="members">
            <MemberManagement
              :search-term-prop="searchTerm"
              :show-guest-labels="true"
              @member-count-update="updateMemberCount"
              @guest-count-update="updateGuestCount"
            />
          </div>

          <div v-else-if="currentView === 'organizations'" key="organizations">
            <OrganizationManagement
              ref="organizationManagementRef"
              :search-term-prop="searchTerm"
              @organization-count-update="updateOrganizationCount"
            />
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed, ref, onMounted, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { NBadge, NButton, NIcon, NInput, NSpin, NTabPane, NTabs, NTooltip, useMessage } from 'naive-ui'
  import {
    BusinessOutline as BuildingIcon,
    PeopleOutline as PeopleIcon,
    SearchOutline as SearchIcon,
    CloseOutline as CloseIcon,
    AddOutline as AddIcon,
    PersonOutline as PersonIcon,
    RefreshOutline as RefreshIcon
  } from '@vicons/ionicons5'
  import MemberManagement from '@/components/team/MemberManagement.vue'
  import OrganizationManagement from '@/components/team/OrganizationManagement.vue'
  import { usePermissions } from '@/composables/usePermissions'
  import apiClient from '@/services/apiClient'

  // Router and Permissions
  const router = useRouter()
  const message = useMessage()
  const { canEditMember } = usePermissions()

  // State
  const currentView = ref('members')
  const searchTerm = ref('')
  const memberCount = ref(0)
  const organizationCount = ref(0)
  const guestCount = ref(0)
  const loadingStats = ref(true)

  // Refs for child components
  const organizationManagementRef = ref(null)

  // Computed
  const searchPlaceholder = computed(() => {
    const placeholders = {
      members: '搜尋成員姓名、學號或組織...',
      organizations: '搜尋組織名稱或聯絡人...'
    }
    return placeholders[currentView.value] || '搜尋...'
  })

  // Methods
  const handleTabChange = value => {
    searchTerm.value = ''
  }

  const clearSearch = () => {
    searchTerm.value = ''
  }

  const goToAddMember = () => {
    router.push({ name: 'AddMember' })
  }

  const goToAddOrganization = async () => {
    if (currentView.value !== 'organizations') {
      currentView.value = 'organizations'
      await nextTick()
    }

    await nextTick()

    if (organizationManagementRef.value && organizationManagementRef.value.openFormModal) {
      organizationManagementRef.value.openFormModal()
    } else {
      message.error('組織管理組件載入中，請稍後再試')
    }
  }

  // 統計數據更新方法（接收子組件事件）
  const updateMemberCount = count => {
    memberCount.value = count
    console.log('📊 子組件更新成員數量:', count)
  }

  const updateOrganizationCount = count => {
    organizationCount.value = count
    console.log('📊 子組件更新組織數量:', count)
  }

  const updateGuestCount = count => {
    guestCount.value = count
    console.log('📊 子組件更新訪客數量:', count)
  }

  // 主要統計數據載入方法
  const loadStatistics = async () => {
    loadingStats.value = true

    try {
      console.log('🔄 開始載入統計數據...')

      // 並發請求獲取統計數據
      const [membersResponse, organizationsResponse] = await Promise.all([
        // 獲取成員數據
        apiClient.get('/members', { params: { include_inactive: true, include_guests: true } }),
        // 獲取組織數據
        apiClient.get('/organizations')
      ])

      // 處理成員統計
      const members = membersResponse.data || []
      const guests = members.filter(member => member.user?.role === 'guest' || member.is_guest)
      const regularMembers = members.filter(member => member.user?.role !== 'guest' && !member.is_guest)

      memberCount.value = regularMembers.length
      guestCount.value = guests.length

      // 處理組織統計
      const organizations = organizationsResponse.data || []
      organizationCount.value = organizations.length

      console.log('✅ 統計數據載入完成:', {
        members: memberCount.value,
        guests: guestCount.value,
        organizations: organizationCount.value
      })
    } catch (error) {
      console.error('❌ 載入統計數據失敗:', error)
      message.error('載入統計數據失敗，請稍後重試')

      // 設置預設值
      memberCount.value = 0
      guestCount.value = 0
      organizationCount.value = 0
    } finally {
      loadingStats.value = false
    }
  }

  // 刷新統計數據
  const refreshStats = async () => {
    await loadStatistics()
    message.success('統計數據已更新')
  }

  // Lifecycle
  onMounted(async () => {
    console.log('🚀 管理中心頁面初始化')
    await loadStatistics()
  })
</script>

<style scoped>
  .management-center-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 2rem;
    font-family:
      'Inter',
      'SF Pro Display',
      -apple-system,
      BlinkMacSystemFont,
      sans-serif;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  /* 1. 標題 + 統計卡片 */
  .page-header {
    /* 保持原有樣式 */
  }

  .header-content {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 2.5rem;
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.1),
      0 1px 0 rgba(255, 255, 255, 0.5) inset;
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
  }

  .title-section {
    flex: 1;
  }

  .page-title {
    font-size: 2.75rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(135deg, #e60012 0%, #ff6b6b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
  }

  /* 統計卡片樣式 */
  .stats-cards {
    display: flex;
    gap: 1.5rem;
  }

  .stat-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.3);
    transition: all 0.3s ease;
    min-width: 120px;
    position: relative;
  }

  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .members-stat .stat-icon {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .organizations-stat .stat-icon {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }

  .guests-stat .stat-icon {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    color: #8b4513;
  }

  .stat-content {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .stat-number {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a202c;
    line-height: 1;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
  }

  .stat-loading {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    opacity: 0.6;
  }

  /* 2. 搜尋區域 */
  .search-section {
    /* 新的搜尋區域 */
  }

  .search-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .modern-search {
    flex: 1;
    border-radius: 16px;
  }

  :deep(.modern-search .n-input__input-el) {
    border-radius: 16px;
    font-size: 1rem;
    padding: 0.75rem 1rem;
  }

  :deep(.modern-search.n-input--focus) {
    box-shadow: 0 0 0 3px rgba(230, 0, 18, 0.1);
  }

  .clear-search-btn {
    color: #9ca3af;
  }

  .refresh-btn {
    border-radius: 16px;
    padding: 0.75rem;
    background: rgba(148, 163, 184, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.2);
    transition: all 0.3s ease;
  }

  .refresh-btn:hover {
    background: rgba(148, 163, 184, 0.2);
    transform: translateY(-1px);
  }

  /* 3. 主要內容區域 */
  .main-content-section {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .content-header {
    padding: 1.5rem 2rem 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
    margin-bottom: 1.5rem;
  }

  .content-tabs {
    flex: 1;
  }

  .tab-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
  }

  .tab-icon {
    transition: transform 0.2s ease;
  }

  .tab-text {
    font-weight: 600;
    font-size: 0.875rem;
  }

  :deep(.content-tabs .n-tabs-tab--active .tab-icon) {
    transform: scale(1.1);
    color: #e60012;
  }

  :deep(.content-tabs .n-tabs-tab) {
    border-radius: 12px !important;
    transition: all 0.3s ease;
  }

  :deep(.content-tabs .n-tabs-tab--active) {
    background: linear-gradient(135deg, rgba(230, 0, 18, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%) !important;
    color: #e60012 !important;
    box-shadow: 0 2px 8px rgba(230, 0, 18, 0.15);
  }

  :deep(.content-tabs .n-tabs-nav) {
    border-bottom: none;
  }

  .header-actions {
    display: flex;
    gap: 1rem;
  }

  .action-btn {
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    background: linear-gradient(135deg, #e60012 0%, #ff6b6b 100%);
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
  }

  .action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(230, 0, 18, 0.4);
    background: linear-gradient(135deg, #cc0010 0%, #ff5252 100%);
  }

  .content-body {
    flex: 1;
    padding: 0 2rem 2rem 2rem;
    overflow: auto;
  }

  /* 過渡動畫 */
  .content-fade-enter-active,
  .content-fade-leave-active {
    transition: all 0.3s ease;
  }

  .content-fade-enter-from {
    opacity: 0;
    transform: translateX(10px);
  }

  .content-fade-leave-to {
    opacity: 0;
    transform: translateX(-10px);
  }

  /* 響應式設計 */
  @media (max-width: 1200px) {
    .management-center-page {
      padding: 1.5rem;
    }

    .stats-cards {
      flex-wrap: wrap;
    }
  }

  @media (max-width: 768px) {
    .management-center-page {
      padding: 1rem;
      gap: 1.5rem;
    }

    .header-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 1.5rem;
      padding: 2rem;
    }

    .page-title {
      font-size: 2.25rem;
    }

    .stats-cards {
      width: 100%;
      justify-content: space-between;
    }

    .stat-card {
      flex: 1;
      min-width: 100px;
      padding: 1rem;
    }

    .search-container {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
    }

    .content-header {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
      padding: 1.5rem 1.5rem 0 1.5rem;
    }

    .header-actions {
      justify-content: center;
    }

    .content-body {
      padding: 0 1.5rem 1.5rem 1.5rem;
    }
  }

  @media (max-width: 480px) {
    .page-title {
      font-size: 1.875rem;
    }

    .stats-cards {
      flex-direction: column;
      gap: 1rem;
    }

    .stat-card {
      min-width: auto;
    }

    .tab-content {
      padding: 0.5rem 1rem;
    }

    .tab-text {
      font-size: 0.8rem;
    }

    .content-header {
      padding: 1rem 1rem 0 1rem;
    }

    .content-body {
      padding: 0 1rem 1rem 1rem;
    }
  }
</style>
