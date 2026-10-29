<template>
  <div v-if="authStore.isAuthenticated" class="user-menu" :class="{ compact }">
    <n-dropdown trigger="click" :options="options" placement="top-start" @select="handleSelect">
      <button class="user-button" type="button">
        <PlayerAvatar
          :id="authStore.user?.member_id"
          :name="authStore.userDisplayName"
          :src="authStore.user?.avatar_url"
          :size="compact ? 34 : 38"
        />
        <span v-if="!compact" class="user-text">
          <span class="user-name">{{ authStore.userDisplayName }}</span>
          <span class="user-role">{{ roleLabel }}</span>
        </span>
      </button>
    </n-dropdown>
  </div>
  <router-link v-else :to="{ name: 'Login' }" class="login-link">
    <n-button type="primary" round :size="compact ? 'small' : 'medium'" :block="!compact">登入</n-button>
  </router-link>
</template>

<script setup>
  import { computed, h } from 'vue'
  import { useRouter } from 'vue-router'
  import { NIcon } from 'naive-ui'
  import { LogOutOutline, PersonCircleOutline } from '@vicons/ionicons5'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { useOptions } from '@/composables/useOptions'
  import { useAuthStore } from '@/stores/authStore'

  defineProps({ compact: { type: Boolean, default: false } })

  const authStore = useAuthStore()
  const router = useRouter()
  const { getRoleDisplay } = useOptions()

  const roleLabel = computed(() => getRoleDisplay(authStore.userRole))
  const icon = component => () => h(NIcon, null, { default: () => h(component) })

  const options = [
    { label: '個人主控台', key: 'profile', icon: icon(PersonCircleOutline) },
    { type: 'divider', key: 'divider' },
    { label: '登出', key: 'logout', icon: icon(LogOutOutline) }
  ]

  const handleSelect = key => {
    if (key === 'profile') router.push({ name: 'EditProfile' })
    if (key === 'logout') authStore.logoutAndRedirect()
  }
</script>

<style scoped>
  .user-button {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 8px;
    border: none;
    border-radius: var(--radius-md);
    background: transparent;
    cursor: pointer;
    text-align: left;
    color: inherit;
    transition: background var(--duration-fast);
  }
  .user-button:hover {
    background: rgba(255, 255, 255, 0.08);
  }
  .compact .user-button {
    padding: 2px;
  }
  .user-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .user-name {
    font-weight: 700;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .user-role {
    font-size: 12px;
    opacity: 0.7;
  }
  .login-link {
    display: block;
  }
</style>
