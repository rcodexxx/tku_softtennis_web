<template>
  <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="submit">
    <n-form-item label="目前密碼" path="old_password">
      <n-input v-model:value="form.old_password" type="password" show-password-on="click" />
    </n-form-item>
    <n-form-item label="新密碼" path="new_password">
      <n-input v-model:value="form.new_password" type="password" show-password-on="click" placeholder="至少 6 個字元" />
    </n-form-item>
    <n-form-item label="確認新密碼" path="confirm_password">
      <n-input v-model:value="form.confirm_password" type="password" show-password-on="click" @keyup.enter="submit" />
    </n-form-item>
    <n-button type="primary" block attr-type="submit" :loading="submitting">更新密碼</n-button>
  </n-form>
</template>

<script setup>
  import { reactive, ref } from 'vue'
  import { useMessage } from 'naive-ui'
  import { authApi } from '@/api'

  const emit = defineEmits(['changed'])

  const message = useMessage()
  const formRef = ref(null)
  const submitting = ref(false)
  const form = reactive({ old_password: '', new_password: '', confirm_password: '' })

  const rules = {
    old_password: [{ required: true, message: '請輸入目前密碼', trigger: 'blur' }],
    new_password: [
      { required: true, message: '請輸入新密碼', trigger: 'blur' },
      { min: 6, message: '新密碼至少需要 6 個字元', trigger: 'blur' }
    ],
    confirm_password: [
      { required: true, message: '請再輸入一次新密碼', trigger: 'blur' },
      {
        validator: (_, value) => value === form.new_password,
        message: '兩次輸入的密碼不一致',
        trigger: ['blur', 'input']
      }
    ]
  }

  const submit = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }
    submitting.value = true
    try {
      await authApi.changePassword(form.old_password, form.new_password)
      message.success('密碼已更新')
      Object.assign(form, { old_password: '', new_password: '', confirm_password: '' })
      emit('changed')
    } catch (error) {
      message.error(error.response?.data?.message || '修改密碼失敗')
    } finally {
      submitting.value = false
    }
  }
</script>
