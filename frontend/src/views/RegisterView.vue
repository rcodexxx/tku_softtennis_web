<template>
  <AuthLayout title="加入淡江軟網">
    <n-alert v-if="authStore.status.registerError" type="error" class="notice">
      {{ authStore.status.registerError }}
    </n-alert>

    <n-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent="handleRegister">
      <n-form-item path="phone_number" label="手機號碼">
        <n-input
          v-model:value="form.phone_number"
          placeholder="09 開頭的 10 位數字"
          maxlength="10"
          @keyup.enter="handleRegister"
        >
          <template #prefix><n-icon :component="Mobile" /></template>
        </n-input>
      </n-form-item>
      <n-alert type="warning" :show-icon="false" class="hint">
        初始密碼與手機號碼相同，註冊後請到個人主控台修改密碼。
      </n-alert>
      <n-button type="primary" block size="large" attr-type="submit" :loading="authStore.status.registering">
        建立帳號
      </n-button>
    </n-form>

    <p class="switch">
      已經有帳號了？
      <router-link :to="{ name: 'Login' }">登入</router-link>
    </p>
  </AuthLayout>
</template>

<script setup>
  import { reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { Mobile } from '@vicons/carbon'
  import AuthLayout from '@/components/auth/AuthLayout.vue'
  import { useAuthStore } from '@/stores/authStore'

  const authStore = useAuthStore()
  const router = useRouter()
  const message = useMessage()

  const formRef = ref(null)
  const form = reactive({ phone_number: '' })
  const rules = {
    phone_number: [
      { required: true, message: '請輸入手機號碼', trigger: ['input', 'blur'] },
      { pattern: /^09\d{8}$/, message: '手機號碼格式不正確（09 開頭的 10 位數字）', trigger: ['input', 'blur'] }
    ]
  }

  const handleRegister = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }
    if (!(await authStore.register(form.phone_number))) return
    message.success('註冊成功！記得修改初始密碼。', { duration: 5000 })
    router.push({ name: 'EditProfile' })
  }
</script>

<style scoped>
  .notice {
    margin-bottom: 18px;
  }
  .hint {
    margin: -4px 0 20px;
    font-size: 15px;
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
