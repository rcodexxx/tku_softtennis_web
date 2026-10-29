<template>
  <AuthLayout title="歡迎回來" subtitle="登入後即可記錄比賽、查看個人數據。">
    <n-alert v-if="notice" type="info" :show-icon="false" class="notice">{{ notice }}</n-alert>
    <n-alert v-if="authStore.status.loginError" type="error" class="notice">
      {{ authStore.status.loginError }}
    </n-alert>

    <n-form ref="formRef" :model="credentials" :rules="rules" size="large" @submit.prevent="handleLogin">
      <n-form-item path="username" label="帳號">
        <n-input
          v-model:value="credentials.username"
          placeholder="手機號碼或 Email"
          :input-props="{ autocomplete: 'username' }"
        >
          <template #prefix><n-icon :component="PersonOutline" /></template>
        </n-input>
      </n-form-item>
      <n-form-item path="password" label="密碼">
        <n-input
          v-model:value="credentials.password"
          type="password"
          show-password-on="click"
          placeholder="請輸入密碼"
          :input-props="{ autocomplete: 'current-password' }"
          @keyup.enter="handleLogin"
        >
          <template #prefix><n-icon :component="LockClosedOutline" /></template>
        </n-input>
      </n-form-item>
      <n-checkbox v-model:checked="rememberMe" class="remember">記住帳號</n-checkbox>
      <n-button type="primary" block size="large" attr-type="submit" :loading="authStore.status.loggingIn">
        登入
      </n-button>
    </n-form>

    <p class="switch">
      還沒有帳號？
      <router-link :to="{ name: 'Register' }">用手機號碼快速註冊</router-link>
    </p>
  </AuthLayout>
</template>

<script setup>
  import { onMounted, reactive, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { LockClosedOutline, PersonOutline } from '@vicons/ionicons5'
  import AuthLayout from '@/components/auth/AuthLayout.vue'
  import { useAuthStore } from '@/stores/authStore'

  const LAST_USERNAME_KEY = 'lastUsername'

  const authStore = useAuthStore()
  const route = useRoute()
  const router = useRouter()

  const formRef = ref(null)
  const rememberMe = ref(false)
  const notice = ref('')
  const credentials = reactive({ username: '', password: '' })

  const rules = {
    username: [{ required: true, message: '請輸入帳號', trigger: ['input', 'blur'] }],
    password: [{ required: true, message: '請輸入密碼', trigger: ['input', 'blur'] }]
  }

  onMounted(() => {
    authStore.clearLoginError()
    const lastUsername = localStorage.getItem(LAST_USERNAME_KEY)
    if (lastUsername) {
      credentials.username = lastUsername
      rememberMe.value = true
    }
    if (route.query.loggedOut === 'true') notice.value = '您已成功登出。'
    else if (route.query.redirect) notice.value = '請先登入才能使用這個頁面。'
  })

  const handleLogin = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }
    if (!(await authStore.login(credentials))) return
    if (rememberMe.value) localStorage.setItem(LAST_USERNAME_KEY, credentials.username)
    else localStorage.removeItem(LAST_USERNAME_KEY)
    router.push(route.query.redirect || { name: 'Leaderboard' })
  }
</script>

<style scoped>
  .notice {
    margin-bottom: 18px;
  }
  .remember {
    margin: -4px 0 20px;
  }
  .switch {
    margin-top: 28px;
    text-align: center;
    color: var(--color-text-muted);
  }
  .switch a {
    color: var(--color-primary);
    font-weight: 700;
  }
</style>
