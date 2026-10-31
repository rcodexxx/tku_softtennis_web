<template>
  <div class="player-select">
    <n-select
      :value="modelValue"
      :options="options"
      :render-label="renderLabel"
      :placeholder="placeholder"
      filterable
      tag
      clearable
      :on-create="toCreateOption"
      :show-arrow="false"
      size="large"
      @update:value="select"
    />

    <QuickGuestModal v-model:show="creating" :name="pendingName" :organizations="organizations" @created="onCreated" />
  </div>
</template>

<script setup>
  import { computed, h, ref } from 'vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import QuickGuestModal from './QuickGuestModal.vue'
  import { organizationLabel } from '@/utils/player'

  const NEW_PREFIX = 'new:'

  /**
   * 選一位球員：打字搜尋，找不到就直接新增成訪客（對手）。
   * players 是所有可選的球員，excluded 是其他欄位已經選的人。
   */
  const props = defineProps({
    modelValue: { type: Number, default: null },
    players: { type: Array, required: true },
    excluded: { type: Array, default: () => [] },
    organizations: { type: Array, default: () => [] },
    placeholder: { type: String, default: '搜尋或新增球員' }
  })
  const emit = defineEmits(['update:modelValue', 'created'])

  const creating = ref(false)
  const pendingName = ref('')

  const options = computed(() =>
    props.players.map(player => ({
      label: player.name,
      value: player.id,
      player,
      disabled: player.id !== props.modelValue && props.excluded.includes(player.id)
    }))
  )

  const renderLabel = option => {
    if (!option.player) return h('span', { class: 'player-option create' }, option.label)
    const { player } = option
    const sub = [player.is_guest ? '訪客' : null, organizationLabel(player), player.is_a_division ? '甲組' : null]
      .filter(Boolean)
      .join(' · ')
    return h('span', { class: 'player-option' }, [
      h(PlayerAvatar, { id: player.id, name: player.name, src: player.avatar_url, size: 24 }),
      h('span', { class: 'player-option-name' }, player.name),
      sub ? h('span', { class: 'player-option-sub' }, sub) : null
    ])
  }

  // 打了清單裡沒有的名字時，多一個「新增」選項
  const toCreateOption = label => ({ label: `＋ 新增對手「${label}」`, value: `${NEW_PREFIX}${label}` })

  const select = value => {
    if (typeof value === 'string' && value.startsWith(NEW_PREFIX)) {
      pendingName.value = value.slice(NEW_PREFIX.length).trim()
      creating.value = true
      return
    }
    emit('update:modelValue', value ?? null)
  }

  const onCreated = (id, guest) => {
    emit('created', guest)
    emit('update:modelValue', id)
  }
</script>

<style>
  /* 下拉選單會被移到 body 底下，所以不能用 scoped */
  .player-option {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .player-option.create {
    color: var(--accent-text);
    font-weight: 600;
  }
  .player-option-name {
    font-weight: 600;
  }
  .player-option-sub {
    font-size: 13px;
    color: var(--ink-3);
  }
</style>
