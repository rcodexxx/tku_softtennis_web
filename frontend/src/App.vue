<template>
  <n-config-provider
    :theme="isDark ? darkTheme : null"
    :theme-overrides="overrides"
    :locale="zhTW"
    :date-locale="dateZhTW"
  >
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <router-view v-if="route.meta.fullscreen" />

          <div v-else class="app-shell" :class="{ mobile: isMobile, 'with-tabs': showTabs }">
            <AppSidebar v-if="!isMobile" />
            <AppTopBar v-else />

            <main class="app-main">
              <div class="app-content">
                <router-view v-slot="{ Component }">
                  <transition name="page" mode="out-in">
                    <component :is="Component" :key="route.fullPath" />
                  </transition>
                </router-view>
              </div>
            </main>

            <AppBottomNav v-if="showTabs" />
          </div>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
  import { computed, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { darkTheme, dateZhTW, zhTW } from 'naive-ui'
  import { useWindowSize } from '@vueuse/core'
  import AppBottomNav from '@/components/layout/AppBottomNav.vue'
  import AppSidebar from '@/components/layout/AppSidebar.vue'
  import AppTopBar from '@/components/layout/AppTopBar.vue'
  import { useNavItems } from '@/composables/useNavItems'
  import { useTheme } from '@/composables/useTheme'
  import { themeOverridesFor } from '@/config/theme'
  import { useAuthStore } from '@/stores/authStore'
  import '@/styles/base.css'

  const MOBILE_BREAKPOINT = 900

  const route = useRoute()
  const authStore = useAuthStore()
  const { width } = useWindowSize()
  const { theme, isDark } = useTheme()
  const overrides = computed(() => themeOverridesFor(theme.value))

  const { items: navItems } = useNavItems()

  const isMobile = computed(() => width.value < MOBILE_BREAKPOINT)
  // 只有一個入口（一般成員、未登入）時不需要底部分頁列
  const showTabs = computed(() => isMobile.value && navItems.value.length > 1)

  onMounted(() => {
    // 用伺服器上的最新資料更新本地快取的使用者
    if (authStore.accessToken) authStore.fetchCurrentUser()
  })
</script>

<style scoped>
  .app-shell {
    min-height: 100vh;
  }
  .app-main {
    margin-left: var(--sidebar-width);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .app-content {
    flex: 1;
    width: 100%;
    max-width: var(--content-max-width);
    margin: 0 auto;
    padding: 32px 32px 24px;
  }
  .mobile .app-main {
    margin-left: 0;
  }
  .with-tabs .app-main {
    padding-bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
  }
  .mobile .app-content {
    padding: 16px 14px;
  }
</style>
