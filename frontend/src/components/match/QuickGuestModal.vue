<template>
  <n-modal v-model:show="show" preset="card" title="新增對手" style="width: min(420px, 94vw)" @after-leave="reset">
    <n-form label-placement="top">
      <n-form-item label="姓名">
        <n-input v-model:value="draft.name" maxlength="80" />
      </n-form-item>
      <n-form-item label="性別">
        <n-radio-group v-model:value="draft.gender">
          <n-radio-button value="male">男</n-radio-button>
          <n-radio-button value="female">女</n-radio-button>
        </n-radio-group>
      </n-form-item>
      <n-form-item label="組別">
        <n-switch v-model:value="draft.is_a_division">
          <template #checked>甲組</template>
          <template #unchecked>一般組</template>
        </n-switch>
      </n-form-item>
      <n-form-item label="學校／組織（選填）">
        <n-select v-model:value="draft.organization_id" :options="organizationOptions" clearable filterable />
      </n-form-item>
    </n-form>
    <template #footer>
      <div class="modal-footer">
        <n-button @click="show = false">取消</n-button>
        <n-button type="primary" :loading="saving" :disabled="!draft.name?.trim() || !draft.gender" @click="create">
          新增並選擇
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
  import { computed, reactive, ref, watch } from 'vue'
  import { useMessage } from 'naive-ui'
  import { guestsApi } from '@/api'

  /**
   * 記錄比賽時當場新增對手（訪客）。成功時 emit created(id, guest)；
   * 同名訪客已存在時直接回傳那位的 id（guest 為 null，呼叫端重新載入名單即可）。
   */
  const show = defineModel('show', { type: Boolean, default: false })
  const props = defineProps({
    name: { type: String, default: '' },
    organizations: { type: Array, default: () => [] }
  })
  const emit = defineEmits(['created'])

  const message = useMessage()
  const saving = ref(false)
  const draft = reactive({ name: '', gender: null, is_a_division: false, organization_id: null })
  const organizationOptions = computed(() => props.organizations.map(org => ({ label: org.name, value: org.id })))

  watch(show, open => {
    if (open) draft.name = props.name
  })

  const create = async () => {
    saving.value = true
    try {
      const guest = await guestsApi.create({
        name: draft.name.trim(),
        gender: draft.gender,
        is_a_division: draft.is_a_division,
        organization_id: draft.organization_id
      })
      emit('created', guest.id, guest)
      show.value = false
    } catch (error) {
      const existing = error.response?.data?.details?.existing_guest_id
      if (existing) {
        emit('created', existing, null)
        show.value = false
      } else {
        message.error(error.response?.data?.message || '新增失敗')
      }
    } finally {
      saving.value = false
    }
  }

  const reset = () => Object.assign(draft, { name: '', gender: null, is_a_division: false, organization_id: null })
</script>

<style scoped>
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
