<template>
  <div class="member-form">
    <n-button quaternary class="back" @click="router.back()">
      <template #icon><n-icon :component="ArrowLeft" /></template>
      返回
    </n-button>
    <PageHeader :eyebrow="isEdit ? 'Edit player' : 'New player'" :title="isEdit ? '編輯球員' : '新增球員'" />

    <n-spin :show="loading">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top" class="sections">
        <section v-if="isEdit && member" class="card identity">
          <AvatarUploader
            :member-id="member.id"
            :name="member.name"
            :src="member.avatar_url"
            :size="80"
            @updated="member = $event"
          />
          <div class="identity-text">
            <h2 class="identity-name">{{ member.name }}</h2>
            <p class="identity-sub">點頭像可以換照片</p>
          </div>
          <n-button v-if="kind === 'guest'" size="small" @click="promote">轉為校內球員</n-button>
        </section>

        <!-- 新增時先選身分 -->
        <section v-if="!isEdit" class="card">
          <div class="segments" role="radiogroup" aria-label="身分">
            <button
              v-for="option in KINDS"
              :key="option.value"
              type="button"
              class="segment"
              :class="{ active: kind === option.value }"
              @click="setKind(option.value)"
            >
              <span class="segment-title">{{ option.label }}</span>
              <span class="segment-text">{{ option.text }}</span>
            </button>
          </div>
        </section>

        <section class="card">
          <h3 class="hud-label section-title">球員資料</h3>
          <n-grid :cols="2" :x-gap="16" responsive="screen" item-responsive>
            <n-form-item-gi span="2 m:1" label="姓名" path="name">
              <n-input v-model:value="form.name" maxlength="80" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="性別" path="gender">
              <n-radio-group v-model:value="form.gender">
                <n-radio-button v-for="option in genderOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </n-radio-button>
              </n-radio-group>
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="組別">
              <n-switch v-model:value="form.is_a_division">
                <template #checked>甲組</template>
                <template #unchecked>一般組</template>
              </n-switch>
            </n-form-item-gi>
            <n-form-item-gi
              span="2 m:1"
              :label="kind === 'guest' ? '學校／組織（選填）' : '所屬組織'"
              path="organization_id"
            >
              <n-select
                v-model:value="form.organization_id"
                :options="organizationOptions"
                :loading="organizationLoading"
                clearable
                filterable
              />
            </n-form-item-gi>
            <template v-if="kind === 'player'">
              <n-form-item-gi span="2 m:1" label="學號" path="student_id">
                <n-input v-model:value="form.student_id" maxlength="20" />
              </n-form-item-gi>
              <n-form-item-gi span="2 m:1" label="擅長位置" path="position">
                <n-radio-group v-model:value="form.position">
                  <n-radio-button v-for="option in positionOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </n-radio-button>
                </n-radio-group>
              </n-form-item-gi>
              <n-form-item-gi span="2 m:1" label="入隊日期" path="joined_date_ts">
                <n-date-picker v-model:value="form.joined_date_ts" type="date" clearable class="full" />
              </n-form-item-gi>
              <n-form-item-gi v-if="isEdit" span="2 m:1" label="離隊日期" path="leaved_date_ts">
                <n-date-picker v-model:value="form.leaved_date_ts" type="date" clearable class="full" />
              </n-form-item-gi>
            </template>
            <n-form-item-gi span="2" label="備註" path="notes">
              <n-input v-model:value="form.notes" type="textarea" :rows="2" />
            </n-form-item-gi>
          </n-grid>
        </section>

        <!-- 登入帳號：選填，只有要讓他自己登入時才需要 -->
        <section v-if="kind === 'player'" class="card">
          <div class="account-head">
            <h3 class="hud-label section-title">登入帳號</h3>
            <n-switch v-if="!isEdit" v-model:value="withAccount" size="small">
              <template #checked>建立帳號</template>
              <template #unchecked>不需要</template>
            </n-switch>
          </div>
          <p v-if="!hasAccount" class="note">
            {{
              isEdit
                ? '沒有登入帳號，一樣能記錄比賽、上排行榜。'
                : '不建立帳號也能記錄比賽、上排行榜；要讓他自己登入時再開。'
            }}
          </p>
          <n-grid v-else :cols="2" :x-gap="16" responsive="screen" item-responsive>
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
              <n-input v-model:value="form.display_name" placeholder="留空則使用姓名" maxlength="50" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="權限" path="role">
              <n-select v-model:value="form.role" :options="roleOptions" :disabled="!authStore.isAdmin" />
            </n-form-item-gi>
          </n-grid>
        </section>
      </n-form>
    </n-spin>

    <footer class="footer">
      <n-button size="large" @click="router.back()">取消</n-button>
      <n-button type="primary" size="large" :loading="saving" @click="save">{{ isEdit ? '儲存' : '建立' }}</n-button>
    </footer>
  </div>
</template>

<script setup>
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { ArrowLeft } from '@vicons/carbon'
  import { guestsApi, membersApi } from '@/api'
  import AvatarUploader from '@/components/base/AvatarUploader.vue'
  import PageHeader from '@/components/base/PageHeader.vue'
  import { useOptions } from '@/composables/useOptions'
  import { useAuthStore } from '@/stores/authStore'
  import { dateToTimestamp, formatDate } from '@/utils/format'

  const KINDS = [
    { value: 'player', label: '校內球員', text: '校隊、校友會的人' },
    { value: 'guest', label: '對手', text: '其他學校或外面一起打的人' }
  ]

  /** 新增或編輯球員：校內球員可以選擇建立登入帳號；對手（訪客）只需要基本資料。 */
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
  const kind = ref('player')
  const promoting = ref(false)
  const withAccount = ref(false)
  const hasAccount = computed(() => (isEdit.value ? Boolean(member.value?.user) : withAccount.value))
  const form = reactive({
    username: '',
    password: '',
    display_name: '',
    role: 'member',
    name: '',
    student_id: '',
    gender: null,
    position: null,
    organization_id: null,
    is_a_division: false,
    joined_date_ts: null,
    leaved_date_ts: null,
    notes: ''
  })

  const rules = computed(() => ({
    username:
      !isEdit.value && hasAccount.value
        ? [
            { required: true, message: '請輸入手機號碼', trigger: 'blur' },
            { pattern: /^09\d{8}$/, message: '手機號碼格式不正確', trigger: 'blur' }
          ]
        : [],
    password: [{ min: 6, message: '密碼至少需要 6 個字元', trigger: 'blur' }],
    name: [{ required: true, message: '請輸入姓名', trigger: 'blur' }],
    gender: [{ required: true, message: '請選擇性別（起始分數依性別而定）', trigger: 'change' }],
    leaved_date_ts: [
      {
        validator: (_, value) => !value || !form.joined_date_ts || value > form.joined_date_ts,
        message: '離隊日期必須晚於入隊日期',
        trigger: 'change'
      }
    ]
  }))

  const setKind = value => {
    kind.value = value
    if (value === 'guest') withAccount.value = false
  }

  const promote = () => {
    kind.value = 'player'
    promoting.value = true
    message.info('儲存後會變成校內球員，比賽紀錄都會保留')
  }

  const basePayload = () => ({
    name: form.name,
    gender: form.gender,
    is_a_division: form.is_a_division,
    organization_id: form.organization_id,
    notes: form.notes || null
  })

  const playerPayload = () => ({
    ...basePayload(),
    student_id: form.student_id || null,
    position: form.position,
    joined_date: formatDate(form.joined_date_ts)
  })

  const save = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }
    saving.value = true
    try {
      let saved
      if (isEdit.value) {
        const data = kind.value === 'guest' ? basePayload() : playerPayload()
        if (kind.value === 'player') data.leaved_date = formatDate(form.leaved_date_ts)
        if (promoting.value) data.is_guest = false
        if (member.value.user) Object.assign(data, { display_name: form.display_name || form.name, role: form.role })
        saved = await membersApi.update(props.memberId, data)
      } else if (kind.value === 'guest') {
        saved = await guestsApi.create(basePayload())
      } else {
        const data = playerPayload()
        if (withAccount.value) {
          Object.assign(data, {
            username: form.username,
            password: form.password || null,
            display_name: form.display_name || form.name,
            role: form.role
          })
        }
        saved = await membersApi.create(data)
      }
      message.success(isEdit.value ? '已儲存' : `已建立「${saved.name}」`)
      router.push({ name: 'Player', params: { id: saved.id } })
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
      kind.value = m.is_guest ? 'guest' : 'player'
      Object.assign(form, {
        username: m.user?.username || '',
        display_name: m.user?.display_name || '',
        role: m.user?.role || 'member',
        name: m.name,
        student_id: m.student_id || '',
        gender: m.gender,
        position: m.position,
        organization_id: m.organization_id,
        is_a_division: m.is_a_division ?? false,
        joined_date_ts: dateToTimestamp(m.joined_date),
        leaved_date_ts: dateToTimestamp(m.leaved_date),
        notes: m.notes || m.guest_notes || ''
      })
    } catch {
      message.error('找不到這位球員')
      router.back()
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .member-form {
    max-width: 860px;
    margin: 0 auto;
  }
  .back {
    margin-bottom: 8px;
  }
  .sections {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .card {
    padding: 18px 20px 4px;
    background: var(--surface);
    border: 1px solid var(--line-soft);
  }
  .identity {
    display: flex;
    align-items: center;
    gap: 18px;
    padding-bottom: 18px;
  }
  .identity-text {
    flex: 1;
  }
  .identity-name {
    margin: 0;
    font-size: 22px;
    color: var(--ink);
  }
  .identity-sub {
    margin: 4px 0 0;
    font-size: 14px;
    color: var(--ink-3);
  }
  .segments {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    padding-bottom: 14px;
  }
  .segment {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 14px 16px;
    border: 1px solid var(--line);
    background: transparent;
    color: var(--ink);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .segment.active {
    border-color: var(--ink);
    background: var(--ink);
    color: var(--bg);
  }
  .segment-title {
    font-size: 17px;
    font-weight: 700;
  }
  .segment-text {
    font-size: 14px;
    opacity: 0.75;
  }
  .section-title {
    margin: 0 0 14px;
  }
  .account-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .account-head .section-title {
    margin: 0;
  }
  .note {
    margin: 12px 0 16px;
    color: var(--ink-3);
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
    background: linear-gradient(transparent, var(--bg) 30%);
  }
  @media (max-width: 900px) {
    .footer {
      bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    }
  }
</style>
