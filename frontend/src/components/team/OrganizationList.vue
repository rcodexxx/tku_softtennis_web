<template>
  <div class="organizations">
    <div class="toolbar">
      <n-input v-model:value="keyword" placeholder="搜尋組織" clearable round class="search">
        <template #prefix><n-icon :component="Search" /></template>
      </n-input>
      <n-button v-if="canManageOrganization" type="primary" @click="openForm()">
        <template #icon><n-icon :component="Add" /></template>
        新增組織
      </n-button>
    </div>

    <div v-if="loading" class="grid">
      <n-skeleton v-for="n in 4" :key="n" height="150px" :sharp="false" />
    </div>
    <n-empty v-else-if="!filtered.length" description="還沒有組織" class="empty" />
    <div v-else class="grid">
      <article v-for="(org, index) in filtered" :key="org.id" class="org-card stagger-in" :style="{ '--i': index }">
        <header class="org-head">
          <span class="badge">{{ (org.short_name || org.name).slice(0, 2) }}</span>
          <div class="org-title">
            <h3>{{ org.name }}</h3>
            <span v-if="org.short_name" class="short">{{ org.short_name }}</span>
          </div>
          <div v-if="canManageOrganization" class="actions">
            <n-button quaternary circle size="small" title="編輯" @click="openForm(org)">
              <template #icon><n-icon :component="Edit" /></template>
            </n-button>
            <n-button quaternary circle size="small" type="error" title="刪除" @click="confirmDelete(org)">
              <template #icon><n-icon :component="TrashCan" /></template>
            </n-button>
          </div>
        </header>
        <p v-if="org.description" class="description">{{ org.description }}</p>
        <footer class="org-foot">
          <span class="members"
            ><b class="num">{{ org.members_count }}</b> 位成員</span
          >
          <span v-if="org.contact_person" class="contact">
            聯絡人 {{ org.contact_person }}<template v-if="org.contact_phone"> · {{ org.contact_phone }}</template>
          </span>
        </footer>
      </article>
    </div>

    <n-modal
      v-model:show="formOpen"
      preset="card"
      :title="editing ? '編輯組織' : '新增組織'"
      style="width: min(520px, 94vw)"
    >
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
        <n-grid :cols="2" :x-gap="12">
          <n-form-item-gi :span="2" label="組織名稱" path="name">
            <n-input v-model:value="form.name" maxlength="100" />
          </n-form-item-gi>
          <n-form-item-gi label="簡稱" path="short_name">
            <n-input v-model:value="form.short_name" maxlength="30" placeholder="例如 TKU" />
          </n-form-item-gi>
          <n-form-item-gi label="聯絡人" path="contact_person">
            <n-input v-model:value="form.contact_person" maxlength="50" />
          </n-form-item-gi>
          <n-form-item-gi label="聯絡電話" path="contact_phone">
            <n-input v-model:value="form.contact_phone" maxlength="30" />
          </n-form-item-gi>
          <n-form-item-gi label="聯絡 Email" path="contact_email">
            <n-input v-model:value="form.contact_email" />
          </n-form-item-gi>
          <n-form-item-gi :span="2" label="描述" path="description">
            <n-input v-model:value="form.description" type="textarea" :rows="3" />
          </n-form-item-gi>
        </n-grid>
      </n-form>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="formOpen = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="save">儲存</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, reactive, ref } from 'vue'
  import { useDialog, useMessage } from 'naive-ui'
  import { Add, Edit, Search, TrashCan } from '@vicons/carbon'
  import { organizationsApi } from '@/api'
  import { usePermissions } from '@/composables/usePermissions'

  const FIELDS = ['name', 'short_name', 'description', 'contact_person', 'contact_email', 'contact_phone']

  const props = defineProps({
    organizations: { type: Array, required: true },
    loading: { type: Boolean, default: false }
  })
  const emit = defineEmits(['changed'])

  const dialog = useDialog()
  const message = useMessage()
  const { canManageOrganization } = usePermissions()

  const keyword = ref('')
  const formOpen = ref(false)
  const editing = ref(null)
  const saving = ref(false)
  const formRef = ref(null)
  const form = reactive(Object.fromEntries(FIELDS.map(field => [field, ''])))

  const rules = {
    name: [{ required: true, message: '請輸入組織名稱', trigger: 'blur' }],
    contact_email: [{ type: 'email', message: 'Email 格式不正確', trigger: 'blur' }]
  }

  const filtered = computed(() => {
    const term = keyword.value.trim().toLowerCase()
    if (!term) return props.organizations
    return props.organizations.filter(org =>
      [org.name, org.short_name, org.contact_person].some(value => (value || '').toLowerCase().includes(term))
    )
  })

  const openForm = (org = null) => {
    editing.value = org
    FIELDS.forEach(field => (form[field] = org?.[field] || ''))
    formOpen.value = true
  }

  const save = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }
    saving.value = true
    try {
      const payload = Object.fromEntries(FIELDS.map(field => [field, form[field]?.trim() || null]))
      if (editing.value) await organizationsApi.update(editing.value.id, payload)
      else await organizationsApi.create(payload)
      message.success(editing.value ? '組織已更新' : '組織已新增')
      formOpen.value = false
      emit('changed')
    } catch (error) {
      message.error(error.response?.data?.message || '儲存失敗')
    } finally {
      saving.value = false
    }
  }

  const confirmDelete = org => {
    dialog.error({
      title: `刪除 ${org.name}`,
      content: org.members_count
        ? `這個組織還有 ${org.members_count} 位成員，需先把成員移到其他組織。`
        : '確定要刪除這個組織嗎？',
      positiveText: '刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await organizationsApi.remove(org.id)
          message.success('組織已刪除')
          emit('changed')
        } catch (error) {
          message.error(error.response?.data?.message || '刪除失敗')
        }
      }
    })
  }
</script>

<style scoped>
  .toolbar {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
  }
  .search {
    width: 260px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 14px;
  }
  .empty {
    padding: 48px 0;
  }
  .org-card {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 18px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
  }
  .org-head {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .badge {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--ink);
    color: var(--bg);
    font-weight: 800;
  }
  .org-title {
    flex: 1;
    min-width: 0;
  }
  .org-title h3 {
    margin: 0;
    font-size: 16px;
    color: var(--blue-900);
  }
  .short {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .actions {
    display: flex;
  }
  .description {
    margin: 0;
    font-size: 13px;
    color: var(--gray-700);
  }
  .org-foot {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px dashed var(--color-border);
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .members b {
    font-size: 20px;
    color: var(--blue-700);
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
  @media (max-width: 640px) {
    .search {
      flex: 1;
      width: auto;
    }
  }
</style>
