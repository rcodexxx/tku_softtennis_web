<template>
  <n-drawer
    :show="show"
    :width="isMobile ? '100%' : 460"
    placement="right"
    @update:show="value => emit('update:show', value)"
  >
    <n-drawer-content title="編輯個人資料" closable>
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
        <h3 class="section">帳號</h3>
        <n-form-item label="顯示暱稱" path="display_name">
          <n-input v-model:value="form.display_name" placeholder="排行榜與選單顯示的名字" maxlength="50" />
        </n-form-item>
        <n-form-item label="電子郵件" path="email">
          <n-input v-model:value="form.email" placeholder="可用來登入" />
        </n-form-item>

        <template v-if="hasMember">
          <h3 class="section">球員資料</h3>
          <n-form-item label="真實姓名" path="name">
            <n-input v-model:value="form.name" maxlength="80" />
          </n-form-item>
          <n-form-item label="學號" path="student_id">
            <n-input v-model:value="form.student_id" placeholder="7 到 9 位數字" />
          </n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="性別" path="gender">
              <n-select v-model:value="form.gender" :options="genderOptions" clearable />
            </n-form-item-gi>
            <n-form-item-gi label="擅長位置" path="position">
              <n-select v-model:value="form.position" :options="positionOptions" clearable />
            </n-form-item-gi>
          </n-grid>
          <n-form-item label="所屬組織" path="organization_id">
            <n-select
              v-model:value="form.organization_id"
              :options="organizationOptions"
              :loading="organizationLoading"
              clearable
              filterable
            />
          </n-form-item>
        </template>
      </n-form>

      <template #footer>
        <n-button @click="emit('update:show', false)">取消</n-button>
        <n-button type="primary" :loading="saving" class="save" @click="save">儲存</n-button>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>
  import { computed, reactive, ref, watch } from 'vue'
  import { useMessage } from 'naive-ui'
  import { useWindowSize } from '@vueuse/core'
  import { profileApi } from '@/api'
  import { useOptions } from '@/composables/useOptions'

  const props = defineProps({
    show: { type: Boolean, default: false },
    profile: { type: Object, required: true }
  })
  const emit = defineEmits(['update:show', 'saved'])

  const message = useMessage()
  const { width } = useWindowSize()
  const { genderOptions, positionOptions, organizationOptions, organizationLoading, loadOrganizationOptions } =
    useOptions()

  const formRef = ref(null)
  const saving = ref(false)
  const form = reactive({})
  const isMobile = computed(() => width.value < 600)
  const hasMember = computed(() => Boolean(props.profile.member))

  const rules = {
    email: [{ type: 'email', message: '電子郵件格式不正確', trigger: 'blur' }],
    name: [{ required: true, message: '請輸入姓名', trigger: 'blur' }],
    student_id: [{ pattern: /^\d{7,9}$/, message: '學號必須是 7 到 9 位數字', trigger: 'blur' }]
  }

  watch(
    () => props.show,
    show => {
      if (!show) return
      const { member } = props.profile
      Object.assign(form, {
        display_name: props.profile.display_name || '',
        email: props.profile.email || '',
        name: member?.name || '',
        student_id: member?.student_id || '',
        gender: member?.gender || null,
        position: member?.position || null,
        organization_id: member?.organization_id || null
      })
      loadOrganizationOptions()
    },
    { immediate: true }
  )

  const save = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }
    saving.value = true
    try {
      const payload = { display_name: form.display_name, email: form.email }
      if (hasMember.value) {
        Object.assign(payload, {
          name: form.name,
          student_id: form.student_id,
          gender: form.gender,
          position: form.position,
          organization_id: form.organization_id
        })
      }
      emit('saved', await profileApi.update(payload))
      message.success('個人資料已更新')
      emit('update:show', false)
    } catch (error) {
      message.error(error.response?.data?.message || '更新失敗，請稍後再試')
    } finally {
      saving.value = false
    }
  }
</script>

<style scoped>
  .section {
    margin: 4px 0 12px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: var(--color-accent);
  }
  .save {
    margin-left: 8px;
  }
</style>
