<template>
  <div class="directory">
    <div class="toolbar">
      <n-input v-model:value="keyword" placeholder="搜尋姓名、學號或組織" clearable round class="search">
        <template #prefix><n-icon :component="SearchOutline" /></template>
      </n-input>
      <n-radio-group v-model:value="kind" size="small">
        <n-radio-button value="members">隊員</n-radio-button>
        <n-radio-button value="guests">訪客</n-radio-button>
        <n-radio-button value="all">全部</n-radio-button>
      </n-radio-group>
      <n-select
        v-model:value="organizationId"
        :options="organizationOptions"
        placeholder="所有組織"
        clearable
        size="small"
        class="org"
      />
      <label class="toggle">
        <n-switch v-model:value="showInactive" size="small" />
        顯示離隊成員
      </label>
    </div>

    <div v-if="loading" class="grid">
      <n-skeleton v-for="n in 6" :key="n" height="96px" :sharp="false" />
    </div>
    <n-empty v-else-if="!filtered.length" description="沒有符合條件的成員" class="empty" />
    <TransitionGroup v-else name="list" tag="div" class="grid">
      <MemberCard
        v-for="(member, index) in filtered"
        :key="member.id"
        :member="member"
        :can-edit="canEditMember"
        :can-delete="canDeleteMember"
        class="stagger-in"
        :style="{ '--i': Math.min(index, 18) }"
        @edit="row => router.push({ name: 'EditMember', params: { id: row.id } })"
        @delete="confirmDelete"
      />
    </TransitionGroup>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog, useMessage } from 'naive-ui'
  import { SearchOutline } from '@vicons/ionicons5'
  import { membersApi } from '@/api'
  import { usePermissions } from '@/composables/usePermissions'
  import { organizationLabel } from '@/utils/player'
  import MemberCard from './MemberCard.vue'

  const props = defineProps({
    members: { type: Array, required: true },
    organizations: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  })
  const emit = defineEmits(['changed'])

  const router = useRouter()
  const dialog = useDialog()
  const message = useMessage()
  const { canEditMember, canDeleteMember } = usePermissions()

  const keyword = ref('')
  const kind = ref('members')
  const organizationId = ref(null)
  const showInactive = ref(false)

  const organizationOptions = computed(() => props.organizations.map(org => ({ label: org.name, value: org.id })))

  const filtered = computed(() => {
    const term = keyword.value.trim().toLowerCase()
    return props.members.filter(m => {
      if (kind.value === 'members' && m.is_guest) return false
      if (kind.value === 'guests' && !m.is_guest) return false
      if (!showInactive.value && !m.is_active) return false
      if (organizationId.value && m.organization_id !== organizationId.value) return false
      if (!term) return true
      return [m.name, m.student_id, m.user?.display_name, organizationLabel(m)].some(value =>
        (value || '').toLowerCase().includes(term)
      )
    })
  })

  const confirmDelete = member => {
    dialog.error({
      title: `刪除 ${member.name}`,
      content: member.is_guest
        ? '確定要刪除這位訪客嗎？'
        : '確定要刪除這位成員和他的登入帳號嗎？已有比賽紀錄的成員無法刪除，請改為設定離隊日期。',
      positiveText: '刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await membersApi.remove(member.id)
          message.success(`已刪除 ${member.name}`)
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
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }
  .search {
    width: 260px;
  }
  .org {
    width: 180px;
  }
  .toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--gray-700);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 14px;
  }
  .empty {
    padding: 48px 0;
  }
  @media (max-width: 640px) {
    .search,
    .org {
      width: 100%;
    }
  }
</style>
