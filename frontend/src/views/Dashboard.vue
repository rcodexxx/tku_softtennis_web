<template>
  <div class="me-page">
    <n-skeleton v-if="loading" height="180px" />
    <n-result v-else-if="error" status="error" title="無法載入個人資料" :description="error">
      <template #footer><n-button @click="load">重試</n-button></template>
    </n-result>

    <template v-else-if="profile">
      <PlayerProfile v-if="member" :member-id="member.id" editable @avatar-updated="handleAvatarUpdated">
        <template #actions>
          <div class="actions">
            <span class="role">{{ roleLabel }}</span>
            <n-button size="small" @click="showEdit = true">
              <template #icon><n-icon :component="Edit" /></template>
              編輯資料
            </n-button>
            <n-button size="small" @click="showPassword = true">
              <template #icon><n-icon :component="Password" /></template>
              修改密碼
            </n-button>
          </div>
        </template>
      </PlayerProfile>

      <section v-else class="account">
        <span class="hud-label">Account</span>
        <h1 class="account-name">{{ profile.display_name || profile.username }}</h1>
        <p class="account-note">這個帳號沒有對應的球員資料；需要由幹部建立球員資料後，才會出現在排行榜。</p>
        <div class="actions">
          <span class="role">{{ roleLabel }}</span>
          <n-button size="small" @click="showEdit = true">編輯資料</n-button>
          <n-button size="small" @click="showPassword = true">修改密碼</n-button>
        </div>
      </section>

      <ProfileEditDrawer v-model:show="showEdit" :profile="profile" @saved="handleSaved" />
      <n-modal v-model:show="showPassword" preset="card" title="修改密碼" style="width: min(420px, 92vw)">
        <ChangePasswordForm @changed="showPassword = false" />
      </n-modal>
    </template>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { Edit, Password } from '@vicons/carbon'
  import { profileApi } from '@/api'
  import ChangePasswordForm from '@/components/auth/ChangePasswordForm.vue'
  import PlayerProfile from '@/components/player/PlayerProfile.vue'
  import ProfileEditDrawer from '@/components/profile/ProfileEditDrawer.vue'
  import { useOptions } from '@/composables/useOptions'
  import { useAuthStore } from '@/stores/authStore'

  /** 我的：自己的球員頁（可換頭像）加上帳號設定。 */
  const authStore = useAuthStore()
  const { getRoleDisplay } = useOptions()

  const loading = ref(true)
  const error = ref(null)
  const profile = ref(null)
  const showEdit = ref(false)
  const showPassword = ref(false)

  const member = computed(() => profile.value?.member)
  const roleLabel = computed(() => getRoleDisplay(profile.value?.role))

  const load = async () => {
    loading.value = true
    error.value = null
    try {
      profile.value = await profileApi.get()
    } catch (err) {
      error.value = err.response?.data?.message || '請稍後再試'
    } finally {
      loading.value = false
    }
  }

  const syncAuthUser = () => {
    authStore.setUser({
      ...authStore.user,
      display_name: profile.value.display_name,
      avatar_url: member.value?.avatar_url
    })
  }

  const handleSaved = updated => {
    profile.value = updated
    syncAuthUser()
  }

  const handleAvatarUpdated = updatedMember => {
    profile.value = { ...profile.value, member: updatedMember }
    syncAuthUser()
  }

  onMounted(load)
</script>

<style scoped>
  .me-page {
    max-width: 960px;
    margin: 0 auto;
  }
  .actions {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 6px;
  }
  .role {
    padding: 0 8px;
    border: 1px solid var(--accent-soft);
    color: var(--accent-text);
    font-size: 14px;
    font-weight: 600;
  }
  .account {
    padding: 24px;
    border: 1px solid var(--line-soft);
    background: var(--surface);
  }
  .account-name {
    margin: 6px 0;
    font-size: 28px;
    color: var(--ink);
  }
  .account-note {
    color: var(--ink-3);
  }
</style>
