<template>
  <div class="member-form">
    <n-button quaternary class="back" @click="goBack">
      <template #icon><n-icon :component="ArrowLeft" /></template>
      返回團隊管理
    </n-button>
    <PageHeader :eyebrow="isEdit ? 'EDIT MEMBER' : 'NEW MEMBER'" :title="isEdit ? '編輯成員' : '新增成員'" />

    <n-spin :show="loading">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top" class="sections">
        <section v-if="isEdit && member" class="card identity">
          <AvatarUploader
            :member-id="member.id"
            :name="member.name"
            :src="member.avatar_url"
            :size="88"
            @updated="member = $event"
          />
          <div>
            <h2 class="identity-name">{{ member.name }}</h2>
            <p class="identity-sub">點擊頭像可以上傳照片（JPG、PNG、WebP，3MB 以內）</p>
          </div>
        </section>

        <section class="card">
          <h3 class="section-title">登入帳號</h3>
          <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
            <n-form-item-gi span="2 m:1" label="手機號碼（帳號）" path="username">
              <n-input v-model:value="form.username" :disabled="isEdit" placeholder="09 開頭的 10 位數字" />
            </n-form-item-gi>
            <n-form-item-gi v-if="!isEdit" span="2 m:1" label="初始密碼" path="password">
              <n-input
                v-model:value="form.password"
                type="password"
                show-password-on="click"
                placeholder="留空則與手機號碼相同"
              />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="顯示暱稱" path="display_name">
              <n-input v-model:value="form.display_name" placeholder="留空則使用真實姓名" maxlength="50" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="電子郵件" path="email">
              <n-input v-model:value="form.email" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="角色權限" path="role">
              <n-select v-model:value="form.role" :options="roleOptions" :disabled="!authStore.isAdmin" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="帳號狀態">
              <n-switch v-model:value="form.is_active">
                <template #checked>啟用</template>
                <template #unchecked>停用</template>
              </n-switch>
            </n-form-item-gi>
          </n-grid>
        </section>

        <section class="card">
          <h3 class="section-title">球員資料</h3>
          <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
            <n-form-item-gi span="2 m:1" label="真實姓名" path="name">
              <n-input v-model:value="form.name" maxlength="80" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="學號" path="student_id">
              <n-input v-model:value="form.student_id" maxlength="20" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="性別" path="gender">
              <n-radio-group v-model:value="form.gender">
                <n-radio-button v-for="option in genderOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </n-radio-button>
              </n-radio-group>
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="擅長位置" path="position">
              <n-radio-group v-model:value="form.position">
                <n-radio-button v-for="option in positionOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </n-radio-button>
              </n-radio-group>
            </n-form-item-gi>
          </n-grid>
        </section>

        <section class="card">
          <h3 class="section-title">隊籍</h3>
          <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
            <n-form-item-gi span="2 m:1" label="所屬組織" path="organization_id">
              <n-select
                v-model:value="form.organization_id"
                :options="organizationOptions"
                :loading="organizationLoading"
                clearable
                filterable
              />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="入隊日期" path="joined_date_ts">
              <n-date-picker v-model:value="form.joined_date_ts" type="date" clearable class="full" />
            </n-form-item-gi>
            <n-form-item-gi v-if="isEdit" span="2 m:1" label="離隊日期" path="leaved_date_ts">
              <n-date-picker v-model:value="form.leaved_date_ts" type="date" clearable class="full" />
            </n-form-item-gi>
            <n-form-item-gi span="2" label="備註" path="notes">
              <n-input v-model:value="form.notes" type="textarea" :rows="3" />
            </n-form-item-gi>
          </n-grid>
        </section>
      </n-form>
    </n-spin>

    <footer class="footer">
      <n-button size="large" @click="goBack">取消</n-button>
      <n-button type="primary" size="large" :loading="saving" @click="save">{{
        isEdit ? '儲存變更' : '建立成員'
      }}</n-button>
    </footer>
  </div>
</template>

<script setup>
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { ArrowLeft } from '@vicons/carbon'
  import { membersApi } from '@/api'
  import AvatarUploader from '@/components/base/AvatarUploader.vue'
  import PageHeader from '@/components/base/PageHeader.vue'
  import { useOptions } from '@/composables/useOptions'
  import { useAuthStore } from '@/stores/authStore'
  import { dateToTimestamp, formatDate } from '@/utils/format'

  const props = defineProps({
    mode: { type: String, required: true, validator: value => ['add', 'edit'].includes(value) },
    memberId: { type: Number, default: null }
  })

  const router = useRouter()
  const message = useMessage()
  const authStore = useAuthStore()
  const {
    roleOptions: allRoles,
    genderOptions,
    positionOptions,
    organizationOptions,
    organizationLoading,
    loadOrganizationOptions
  } = useOptions()

  const isEdit = computed(() => props.mode === 'edit')
  const roleOptions = allRoles.filter(option => option.value !== 'guest')
  const loading = ref(false)
  const saving = ref(false)
  const formRef = ref(null)
  const member = ref(null)
  const form = reactive({
    username: '',
    password: '',
    display_name: '',
    email: '',
    role: 'member',
    is_active: true,
    name: '',
    student_id: '',
    gender: null,
    position: null,
    organization_id: null,
    joined_date_ts: null,
    leaved_date_ts: null,
    notes: ''
  })

  const rules = computed(() => ({
    username: isEdit.value
      ? []
      : [
          { required: true, message: '請輸入手機號碼', trigger: 'blur' },
          { pattern: /^09\d{8}$/, message: '手機號碼格式不正確', trigger: 'blur' }
        ],
    password: [{ min: 6, message: '密碼至少需要 6 個字元', trigger: 'blur' }],
    email: [{ type: 'email', message: 'Email 格式不正確', trigger: 'blur' }],
    name: [{ required: true, message: '請輸入真實姓名', trigger: 'blur' }],
    leaved_date_ts: [
      {
        validator: (_, value) => !value || !form.joined_date_ts || value > form.joined_date_ts,
        message: '離隊日期必須晚於入隊日期',
        trigger: 'change'
      }
    ]
  }))

  const goBack = () => router.push({ name: 'ManagementCenter' })

  const payload = () => {
    const data = {
      name: form.name,
      student_id: form.student_id || null,
      gender: form.gender,
      position: form.position,
      organization_id: form.organization_id,
      joined_date: formatDate(form.joined_date_ts),
      notes: form.notes || null,
      display_name: form.display_name || form.name,
      email: form.email || null,
      role: form.role,
      is_active: form.is_active
    }
    if (isEdit.value) data.leaved_date = formatDate(form.leaved_date_ts)
    else Object.assign(data, { username: form.username, password: form.password || null })
    return data
  }

  const save = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }
    saving.value = true
    try {
      if (isEdit.value) await membersApi.update(props.memberId, payload())
      else await membersApi.create(payload())
      message.success(isEdit.value ? '成員資料已更新' : '成員已建立')
      goBack()
    } catch (error) {
      const data = error.response?.data
      message.error(data?.details ? Object.values(data.details).flat().join('；') : data?.message || '儲存失敗')
    } finally {
      saving.value = false
    }
  }

  onMounted(async () => {
    loadOrganizationOptions()
    if (!isEdit.value) return
    loading.value = true
    try {
      member.value = await membersApi.get(props.memberId)
      const m = member.value
      Object.assign(form, {
        username: m.user?.username || '',
        display_name: m.user?.display_name || '',
        email: m.user?.email || '',
        role: m.user?.role || 'member',
        is_active: m.user?.is_active ?? true,
        name: m.name,
        student_id: m.student_id || '',
        gender: m.gender,
        position: m.position,
        organization_id: m.organization_id,
        joined_date_ts: dateToTimestamp(m.joined_date),
        leaved_date_ts: dateToTimestamp(m.leaved_date),
        notes: m.notes || ''
      })
    } catch {
      message.error('找不到這位成員')
      goBack()
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .member-form {
    max-width: 880px;
    margin: 0 auto;
  }
  .back {
    margin-bottom: 8px;
  }
  .sections {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .card {
    padding: 20px 22px 4px;
    border-radius: var(--radius-xl);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
  }
  .identity {
    display: flex;
    align-items: center;
    gap: 20px;
    padding-bottom: 20px;
    background: var(--surface-sunk);
  }
  .identity-name {
    margin: 0;
    font-size: 22px;
    color: var(--blue-900);
  }
  .identity-sub {
    margin: 4px 0 0;
    font-size: 13px;
    color: var(--color-text-muted);
  }
  .section-title {
    margin: 0 0 14px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: var(--color-accent);
  }
  .full {
    width: 100%;
  }
  .footer {
    position: sticky;
    bottom: 0;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 16px;
    padding: 12px 0;
    background: linear-gradient(transparent, var(--color-bg) 30%);
  }
  @media (max-width: 640px) {
    .footer {
      bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    }
  }
</style>
