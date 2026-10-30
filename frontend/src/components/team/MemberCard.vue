<template>
  <article class="member-card" :class="{ inactive: !member.is_active }">
    <PlayerAvatar :id="member.id" :name="member.name" :src="member.avatar_url" :size="56" />
    <div class="body">
      <div class="name-row">
        <h3 class="name">{{ member.name }}</h3>
        <span class="role" :class="roleKey">{{ roleLabel }}</span>
      </div>
      <p class="sub">
        <span v-if="member.user?.display_name && member.user.display_name !== member.name"
          >{{ member.user.display_name }} ·
        </span>
        {{ organization || '無組織' }}
        <span v-if="member.student_id"> · {{ member.student_id }}</span>
      </p>
      <div class="stats">
        <span class="score num">{{ formatRating(member.rating) }}</span>
        <span class="status">
          <span class="dot"></span>
          {{ member.is_active ? '在隊' : '已離隊／停用' }}
        </span>
      </div>
    </div>
    <div class="actions">
      <n-button
        v-if="canEdit && !member.is_guest"
        quaternary
        circle
        size="small"
        title="編輯"
        @click="emit('edit', member)"
      >
        <template #icon><n-icon :component="Edit" /></template>
      </n-button>
      <n-button
        v-if="canDelete"
        quaternary
        circle
        size="small"
        type="error"
        title="刪除"
        @click="emit('delete', member)"
      >
        <template #icon><n-icon :component="TrashCan" /></template>
      </n-button>
    </div>
  </article>
</template>

<script setup>
  import { computed } from 'vue'
  import { Edit, TrashCan } from '@vicons/carbon'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { useOptions } from '@/composables/useOptions'
  import { organizationLabel } from '@/utils/player'
  import { formatRating } from '@/utils/rating'

  const props = defineProps({
    member: { type: Object, required: true },
    canEdit: { type: Boolean, default: false },
    canDelete: { type: Boolean, default: false }
  })
  const emit = defineEmits(['edit', 'delete'])

  const { getRoleDisplay } = useOptions()
  const organization = computed(() => organizationLabel(props.member))
  const roleKey = computed(() => (props.member.is_guest ? 'guest' : props.member.user?.role || 'member'))
  const roleLabel = computed(() =>
    props.member.is_guest ? props.member.guest_role_label || '訪客' : getRoleDisplay(props.member.user?.role)
  )
</script>

<style scoped>
  .member-card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    transition:
      transform var(--duration-base) var(--ease-spring),
      box-shadow var(--duration-base);
  }
  .member-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
  }
  .member-card.inactive {
    opacity: 0.6;
  }
  .body {
    flex: 1;
    min-width: 0;
  }
  .name-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .name {
    margin: 0;
    font-size: 16px;
    font-weight: 800;
    color: var(--blue-900);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .role {
    flex-shrink: 0;
    padding: 0 8px;
    border-radius: var(--radius-full);
    font-size: 11px;
    font-weight: 700;
    background: var(--blue-50);
    color: var(--blue-700);
  }
  .role.admin {
    background: var(--red-100);
    color: var(--red-600);
  }
  .role.coach {
    background: var(--green-100);
    color: var(--green-600);
  }
  .role.cadre {
    background: var(--gold-100);
    color: var(--accent-text);
  }
  .role.guest {
    background: var(--gray-100);
    color: var(--gray-500);
  }
  .sub {
    margin: 2px 0 6px;
    font-size: 12px;
    color: var(--color-text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .stats {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .score {
    font-size: 20px;
    font-weight: 700;
    color: var(--blue-700);
  }
  .status {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--gray-500);
  }
  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--green-500);
  }
  .inactive .dot {
    background: var(--gray-400);
  }
  .actions {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
</style>
