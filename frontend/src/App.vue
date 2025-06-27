<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhTW" :date-locale="dateZhTW" style="height: 100%">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <!-- 🎾 裁判模式全屏檢測 -->
          <div v-if="route.name === 'RefereeMode'" style="width: 100vw; height: 100vh; background: #667eea">
            <router-view />
          </div>

          <!-- 原有佈局 - 完全保持不變 -->
          <n-layout v-else style="height: 100vh" :native-scrollbar="false">
            <n-layout-header bordered class="app-header">
              <div class="navbar-content">
                <!-- 桌面版 LOGO -->
                <router-link v-if="!isMobile" to="/" class="navbar-brand-custom"> TKU Soft Tennis Web</router-link>

                <!-- 移動版選單觸發器 -->
                <div v-if="isMobile" class="mobile-nav-trigger">
                  <n-button text class="mobile-menu-btn" @click="showMobileDrawer = true">
                    <n-icon size="28" color="#333">
                      <MenuIcon />
                    </n-icon>
                  </n-button>
                </div>

                <!-- 桌面版橫向選單 -->
                <n-menu
                  v-if="!isMobile"
                  v-model:value="activeMenuKey"
                  mode="horizontal"
                  :options="menuOptions"
                  responsive
                  class="main-nav-menu"
                />

                <!-- 用戶操作區域 -->
                <div class="user-actions-area">
                  <template v-if="authStore.isAuthenticated">
                    <n-dropdown
                      trigger="hover"
                      :options="userDropdownOptions"
                      placement="bottom-end"
                      @select="handleUserDropdownSelect"
                    >
                      <n-button quaternary class="user-display-button">
                        <div class="user-avatar-container">
                          <BaseIdenticon :user="authStore.user" :size="40" />
                        </div>
                        <span class="user-name">{{ authStore.userDisplayName }}</span>
                        <n-icon size="18" class="dropdown-arrow-icon" color="#666">
                          <ChevronDownIcon />
                        </n-icon>
                      </n-button>
                    </n-dropdown>
                  </template>
                  <template v-else>
                    <n-space align="center" :wrap="false" :size="isMobile ? 'small' : 'medium'">
                      <router-link v-slot="{ navigate }" :to="{ name: 'Login' }">
                        <n-button
                          type="primary"
                          :size="isMobile ? 'small' : 'medium'"
                          round
                          class="login-btn"
                          @click="navigate"
                        >
                          登入
                        </n-button>
                      </router-link>
                    </n-space>
                  </template>
                </div>
              </div>
            </n-layout-header>

            <!-- 主要內容區域 -->
            <n-layout-content class="main-layout-content" :content-style="contentStyle" :native-scrollbar="false">
              <n-spin :show="isInitializing" description="載入中...">
                <router-view v-slot="{ Component }">
                  <transition name="fade" mode="out-in">
                    <component :is="Component" :key="$route.fullPath" />
                  </transition>
                </router-view>
              </n-spin>
            </n-layout-content>

            <!-- 頁腳 -->
            <n-layout-footer bordered position="static" class="app-footer">
              <div class="footer-content">
                <span>&copy; {{ currentYear }} TKU Soft Tennis. All Rights Reserved.</span>
                <span v-if="!isMobile" class="footer-separator">|</span>
                <span v-if="!isMobile">Version 1.1.0</span>
              </div>
            </n-layout-footer>
          </n-layout>

          <!-- 移動版側邊選單 -->
          <n-drawer v-model:show="showMobileDrawer" :width="280" placement="left">
            <n-drawer-content title="選單" closable>
              <!-- 移動版 LOGO -->
              <router-link to="/" class="mobile-drawer-brand" @click="handleMobileMenuClick">
                TKU Soft Tennis Web
              </router-link>

              <!-- 移動版選單項目 -->
              <n-menu
                v-model:value="activeMenuKey"
                mode="vertical"
                :options="mobileMenuOptions"
                class="mobile-nav-menu"
                @update:value="handleMobileMenuSelect"
              />

              <!-- 移動版用戶資訊 -->
              <div v-if="authStore.isAuthenticated" class="mobile-user-info">
                <n-divider />
                <div class="mobile-user-profile">
                  <div class="mobile-avatar-container">
                    <svg ref="mobileAvatarSvg" width="40" height="40" class="identicon-svg" data-jdenticon-value="" />
                  </div>
                  <div class="mobile-user-details">
                    <div class="mobile-user-name">{{ authStore.userDisplayName }}</div>
                  </div>
                </div>

                <n-space vertical :size="8" style="margin-top: 1rem">
                  <router-link v-slot="{ navigate }" :to="{ name: 'EditProfile' }">
                    <n-button
                      block
                      ghost
                      class="mobile-action-btn"
                      @click="
                        () => {
                          navigate()
                          handleMobileMenuClick()
                        }
                      "
                    >
                      <template #icon>
                        <n-icon :component="SettingsIcon" />
                      </template>
                      個人主控台
                    </n-button>
                  </router-link>
                  <n-button block type="error" ghost class="mobile-action-btn" @click="handleLogout">
                    <template #icon>
                      <n-icon :component="LogoutIcon" />
                    </template>
                    登出
                  </n-button>
                </n-space>
              </div>

              <!-- 移動版未登入用戶操作 -->
              <div v-else class="mobile-guest-actions">
                <n-divider />
                <n-space vertical :size="8">
                  <router-link v-slot="{ navigate }" :to="{ name: 'Login' }">
                    <n-button
                      block
                      type="primary"
                      class="mobile-action-btn"
                      @click="
                        () => {
                          navigate()
                          handleMobileMenuClick()
                        }
                      "
                    >
                      登入
                    </n-button>
                  </router-link>
                </n-space>
              </div>
            </n-drawer-content>
          </n-drawer>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
  import { computed, h, onMounted, ref, watch } from 'vue'
  import { RouterLink, useRoute, useRouter } from 'vue-router'
  import { useAuthStore } from './stores/authStore.js'
  import { useWindowSize } from '@vueuse/core'
  import BaseIdenticon from '@/components/base/BaseIdenticon.vue'
  import '@/assets/css/main.css'
  import {
    dateZhTW,
    NButton,
    NConfigProvider,
    NDialogProvider,
    NDivider,
    NDrawer,
    NDrawerContent,
    NDropdown,
    NIcon,
    NLayout,
    NLayoutContent,
    NLayoutFooter,
    NLayoutHeader,
    NMenu,
    NMessageProvider,
    NNotificationProvider,
    NSpace,
    NSpin,
    zhTW
  } from 'naive-ui'
  import {
    ChevronDownOutline as ChevronDownIcon,
    ClipboardOutline as RecordMatchIcon,
    ListCircleOutline as MatchManagementIcon,
    LogOutOutline as LogoutIcon,
    MenuOutline as MenuIcon,
    PeopleOutline as TeamManagementIcon,
    PodiumOutline as HomeIcon,
    SettingsOutline as SettingsIcon
  } from '@vicons/ionicons5'

  // 修復後的主題配置
  const themeOverrides = {
    common: {
      primaryColor: '#e60012',
      primaryColorHover: '#cc0010',
      primaryColorPressed: '#b3000e',
      primaryColorSuppl: '#e60012',
      bodyColor: '#f5f5f5',
      textColorBase: '#333333',
      fontSize: '14px'
    },
    Button: {
      textColorPrimary: '#ffffff'
    },
    Menu: {
      // 桌面版橫向選單 - 修復顏色
      itemTextColorHorizontal: '#333333',
      itemIconColorHorizontal: '#333333',
      itemTextColorHoverHorizontal: '#e60012',
      itemIconColorHoverHorizontal: '#e60012',
      itemTextColorActiveHorizontal: '#e60012',
      itemIconColorActiveHorizontal: '#e60012',
      itemColorActiveHorizontal: 'rgba(230, 0, 18, 0.1)',

      // 移動版垂直選單
      itemTextColorVertical: '#333333',
      itemIconColorVertical: '#333333',
      itemTextColorHoverVertical: '#e60012',
      itemIconColorHoverVertical: '#e60012',
      itemTextColorActiveVertical: '#ffffff',
      itemIconColorActiveVertical: '#ffffff',
      itemColorActiveVertical: '#e60012',
      itemColorHoverVertical: 'rgba(230, 0, 18, 0.1)'
    },
    Layout: {},
    Drawer: {
      titleTextColor: '#e60012',
      titleFontSize: '1.2rem'
    },
    Dropdown: {
      optionTextColor: '#333333'
    }
  }

  // Constants - 調整斷點避免768px問題
  const MOBILE_BREAKPOINT = 900 // 提高到900px，避免768px時的問題
  const TABLET_BREAKPOINT = 1024

  // Stores and route
  const authStore = useAuthStore()
  const route = useRoute()
  const router = useRouter()

  // State
  const showMobileDrawer = ref(false)
  const activeMenuKey = ref(route.name)
  const isInitializing = ref(true)

  // 🎾 設備檢測
  const isMobileDevice = ref(false)

  // 響應式設計 - 調整斷點
  const { width } = useWindowSize()
  const isMobile = computed(() => width.value < MOBILE_BREAKPOINT)
  const isTablet = computed(() => width.value >= MOBILE_BREAKPOINT && width.value < TABLET_BREAKPOINT)

  // 動態內容樣式
  const contentStyle = computed(() => ({
    padding: isMobile.value ? '10px' : '20px',
    height: '100%'
  }))

  // 當前年份
  const currentYear = computed(() => new Date().getFullYear())

  // 權限管理
  const hasManagementAccess = computed(
    () => authStore.isAuthenticated && (authStore.isCadre || authStore.isAdmin || authStore.isCoach)
  )

  const isLogin = computed(() => authStore.isAuthenticated)

  // 角色顯示映射
  const roleDisplayMap = {
    admin: '管理員',
    cadre: '幹部',
    coach: '教練',
    member: '隊員',
    guset: '訪客'
  }

  // 🎾 檢查設備類型
  const checkDeviceType = () => {
    const userAgent = navigator.userAgent.toLowerCase()
    const isMobile = /mobile|android|iphone|ipad|tablet/.test(userAgent)
    const hasTouch = 'ontouchstart' in window
    const isSmallScreen = window.innerWidth <= 1024

    isMobileDevice.value = isMobile || (hasTouch && isSmallScreen)
  }

  // 🎾 前往裁判模式
  const goToRefereeMode = () => {
    if (!authStore.isAuthenticated) {
      router.push({ name: 'Login' })
      return
    }

    // 關閉移動選單
    showMobileDrawer.value = false

    router.push({ name: 'RefereeMode' })
  }

  // Watch route changes
  watch(
    () => route.name,
    newName => {
      activeMenuKey.value = newName
      // 在路由變化時自動關閉移動選單
      if (showMobileDrawer.value) {
        showMobileDrawer.value = false
      }
    },
    { immediate: true }
  )

  // Helper functions
  const renderIcon = icon => () => h(NIcon, { color: '#333' }, { default: () => h(icon) })

  const renderRouterLink = (routeName, label) => () =>
    h(
      RouterLink,
      {
        to: { name: routeName },
        style: {
          color: 'inherit',
          textDecoration: 'none',
          display: 'flex',
          alignItems: 'center',
          width: '100%'
        }
      },
      { default: () => label }
    )

  // 桌面版選單選項
  const menuOptions = computed(() =>
    [
      {
        label: renderRouterLink('Leaderboard', '校內排行榜'),
        key: 'Leaderboard',
        icon: renderIcon(HomeIcon)
      },
      {
        label: renderRouterLink('DetailLeaderboard', '詳細數據'),
        key: 'DetailLeaderboard',
        icon: renderIcon(HomeIcon),
        show: isLogin.value
      },
      {
        label: renderRouterLink('RecordMatch', '記錄比賽'),
        key: 'RecordMatch',
        icon: renderIcon(RecordMatchIcon)
      },
      {
        label: renderRouterLink('MatchManagement', '比賽管理中心'),
        key: 'MatchManagement',
        icon: renderIcon(MatchManagementIcon),
        show: hasManagementAccess.value
      },
      {
        label: renderRouterLink('ManagementCenter', '團隊管理中心'),
        key: 'ManagementCenter',
        icon: renderIcon(TeamManagementIcon),
        show: hasManagementAccess.value
      }
    ].filter(option => option.show !== false)
  )

  const mobileMenuOptions = computed(() =>
    [
      {
        label: '校內排行榜',
        key: 'Leaderboard',
        icon: renderIcon(HomeIcon)
      },
      {
        label: '詳細數據',
        key: 'DetailLeaderboard',
        icon: renderIcon(HomeIcon),
        show: hasManagementAccess.value
      },
      {
        label: '記錄比賽',
        key: 'RecordMatch',
        icon: renderIcon(RecordMatchIcon)
      },
      {
        label: '比賽管理中心',
        key: 'MatchManagement',
        icon: renderIcon(MatchManagementIcon),
        show: hasManagementAccess.value
      },
      {
        label: '團隊管理中心',
        key: 'ManagementCenter',
        icon: renderIcon(TeamManagementIcon),
        show: hasManagementAccess.value
      }
    ].filter(option => option.show !== false)
  )

  // 用戶下拉選單選項
  const userDropdownOptions = computed(() => [
    {
      label: () =>
        h(
          RouterLink,
          {
            to: { name: 'EditProfile' },
            style: { color: 'inherit', textDecoration: 'none', display: 'block', width: '100%' }
          },
          { default: () => '個人主控台' }
        ),
      key: 'edit-profile',
      icon: renderIcon(SettingsIcon)
    },
    { type: 'divider', key: 'd1' },
    {
      label: '登出',
      key: 'logout',
      icon: renderIcon(LogoutIcon)
    }
  ])

  // Event handlers
  const handleUserDropdownSelect = key => {
    if (key === 'logout') {
      authStore.logoutAndRedirect()
    }
  }

  const handleMobileMenuClick = () => {
    showMobileDrawer.value = false
  }

  // 修復：移動版選單選擇處理器
  const handleMobileMenuSelect = menuKey => {
    console.log('Mobile menu selected:', menuKey)

    // 關閉抽屜
    showMobileDrawer.value = false

    // 導航到對應頁面
    if (menuKey && typeof menuKey === 'string') {
      try {
        router.push({ name: menuKey })
      } catch (error) {
        console.error('Navigation error:', error)
      }
    }
  }

  const handleLogout = () => {
    showMobileDrawer.value = false
    authStore.logoutAndRedirect()
  }

  // Helper functions
  function getRoleDisplay(roleName) {
    return roleDisplayMap[roleName] || roleName
  }

  // Lifecycle
  onMounted(async () => {
    try {
      // 🎾 檢查設備類型
      checkDeviceType()
      window.addEventListener('resize', checkDeviceType)

      if (authStore.accessToken && !authStore.user) {
        await authStore.fetchCurrentUser()
      }

      activeMenuKey.value = route.name
    } finally {
      isInitializing.value = false
    }
  })
</script>

<!-- 🔧 保持原有樣式完全不變 -->
<style scoped>
  /* === 主要樣式改進 === */
  .mobile-menu-btn {
    padding: 8px;
    border-radius: 8px;
    transition: background-color 0.2s ease;
  }

  .mobile-menu-btn:hover {
    background-color: rgba(51, 51, 51, 0.1);
  }

  .user-actions-area {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .user-display-button {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    border-radius: 12px;
    transition: all 0.2s ease;
    max-width: 280px;
    color: #333 !important;
    height: 56px;
    font-size: 1rem;
  }

  .user-display-button:hover {
    background-color: rgba(51, 51, 51, 0.05) !important;
    color: #e60012 !important;
  }

  .user-avatar-container {
    margin-right: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
  }

  .mobile-avatar-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .identicon-svg {
    border-radius: 50%;
    display: block;
  }

  .user-name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 140px;
    color: inherit;
    font-size: 1rem;
    font-weight: 500;
  }

  .dropdown-arrow-icon {
    opacity: 0.7;
    transition: transform 0.2s ease;
  }

  .user-display-button:hover .dropdown-arrow-icon {
    transform: rotate(180deg);
  }

  /* === 導航選單樣式強化 === */
  .main-nav-menu :deep(.n-menu-item-content) {
    font-weight: 500;
    transition: all 0.2s ease;
    border-radius: 6px;
    margin: 0 2px;
    white-space: nowrap; /* 防止文字換行 */
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .main-nav-menu :deep(.n-menu-item:hover .n-menu-item-content) {
    background-color: rgba(230, 0, 18, 0.08);
    transform: translateY(-1px);
  }

  .main-nav-menu :deep(.n-menu-item--selected .n-menu-item-content) {
    background-color: rgba(230, 0, 18, 0.1);
    font-weight: 600;
  }

  /* === 特殊修復：768px附近的LOGO保護 === */
  @media (min-width: 768px) and (max-width: 899px) {
    .navbar-content {
      justify-content: space-between;
      gap: 0.5rem;
    }

    .main-nav-menu {
      flex-grow: 0 !important; /* 防止選單過度擴展 */
      flex-shrink: 1;
      min-width: 0;
    }

    .navbar-brand-custom {
      flex-shrink: 0; /* 防止LOGO被擠壓 */
      z-index: 10; /* 確保LOGO在最上層 */
    }

    .user-actions-area {
      flex-shrink: 0; /* 防止用戶區域被擠壓 */
    }
  }

  /* === 平板版響應式修復 === */
  @media (min-width: 768px) and (max-width: 1023px) {
    .navbar-brand-custom {
      font-size: 1rem;
      padding: 8px 16px;
      margin-right: 1rem;
    }

    .main-nav-menu :deep(.n-menu-item-content) {
      padding: 10px 12px !important;
      font-size: 0.9rem;
    }

    .user-display-button {
      padding: 0.625rem 1rem;
      max-width: 200px;
      height: 52px;
      font-size: 0.95rem;
    }

    .user-name {
      max-width: 100px;
      font-size: 0.95rem;
    }
  }

  /* === 移動版樣式 === */
  .mobile-nav-menu :deep(.n-menu-item-content) {
    margin: 2px 0;
    border-radius: 8px;
    padding: 16px 20px;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .mobile-nav-menu :deep(.n-menu-item:hover .n-menu-item-content) {
    transform: translateX(4px);
  }

  .mobile-nav-menu :deep(.n-menu-item--selected .n-menu-item-content) {
    background-color: #e60012;
    color: #ffffff;
  }

  .mobile-user-info {
    margin-top: 2rem;
  }

  .mobile-user-profile {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(230, 0, 18, 0.05);
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .mobile-user-details {
    flex: 1;
    min-width: 0;
  }

  .mobile-user-name {
    font-weight: 600;
    color: #1f2937;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .mobile-action-btn {
    height: 44px;
    border-radius: 8px;
    font-weight: 500;
  }

  .mobile-guest-actions {
    margin-top: 2rem;
  }

  /* === 頁腳樣式 === */
  .app-footer {
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
    padding: 1rem 2rem;
  }

  .footer-content {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .footer-separator {
    color: #d1d5db;
  }

  /* === 登入註冊按鈕樣式 === */
  .register-btn,
  .login-btn {
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .register-btn:hover {
    transform: translateY(-1px);
    border-color: #e60012;
    color: #e60012;
  }

  .login-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
  }

  /* === 頁面過渡動畫 === */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }

  /* === 移動版響應式調整 === */
  @media (max-width: 768px) {
    .app-header {
      padding: 0 16px;
      height: 56px;
    }

    .navbar-content {
      height: 100%;
    }

    .mobile-nav-trigger {
      flex-grow: 0;
    }

    .user-actions-area {
      margin-left: auto;
    }

    .user-display-button {
      padding: 0.5rem 0.75rem;
      max-width: 160px;
      height: 48px;
      font-size: 0.9rem;
    }

    .user-name {
      max-width: 80px;
      font-size: 0.9rem;
    }

    .register-btn,
    .login-btn {
      font-size: 0.875rem;
      padding: 0.375rem 0.75rem;
    }

    .footer-content {
      flex-direction: column;
      gap: 0.5rem;
      font-size: 0.8rem;
    }

    .footer-separator {
      display: none;
    }
  }

  @media (max-width: 480px) {
    .app-header {
      padding: 0 12px;
    }

    .user-actions-area .n-space {
      gap: 0.5rem;
    }

    .register-btn,
    .login-btn {
      padding: 0.25rem 0.5rem;
      font-size: 0.8rem;
    }
  }

  /* === 極小螢幕特殊處理 === */
  @media (max-width: 320px) {
    .user-actions-area {
      gap: 0.25rem;
    }

    .register-btn,
    .login-btn {
      padding: 0.2rem 0.4rem;
      font-size: 0.75rem;
      min-width: auto;
    }
  }
</style>
