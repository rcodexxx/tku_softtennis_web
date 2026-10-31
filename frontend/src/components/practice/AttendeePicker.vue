<template>
  <div class="attendee-picker">
    <div class="toolbar">
      <n-input v-model:value="keyword" placeholder="搜尋" clearable size="small" class="search">
        <template #prefix><n-icon :component="Search" /></template>
      </n-input>
      <span class="hud-label">{{ modelValue.length }} 人</span>
      <n-button size="small" @click="selectTeam">全選校隊</n-button>
      <n-button size="small" quaternary @click="emit('update:modelValue', [])">清除</n-button>
    </div>
    <section v-for="group in groups" :key="group.key" class="group">
      <h3 class="hud-label">{{ group.label }}</h3>
      <div class="chips">
        <button
          v-for="player in group.players"
          :key="player.id"
          type="button"
          class="chip"
          :class="{ active: selected.has(player.id) }"
          :aria-pressed="selected.has(player.id)"
          @click="toggle(player.id)"
        >
          <PlayerAvatar :id="player.id" :name="player.name" :src="player.avatar_url" :size="24" />
          {{ player.name }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { Search } from '@vicons/carbon'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'

  const GROUPS = [
    { key: 'team', label: '校隊' },
    { key: 'alumni', label: '校友會' },
    { key: 'others', label: '其他' }
  ]

  /** 勾選到場的人；players 需帶 roster_category。 */
  const props = defineProps({
    modelValue: { type: Array, required: true },
    players: { type: Array, required: true }
  })
  const emit = defineEmits(['update:modelValue'])

  const keyword = ref('')
  const selected = computed(() => new Set(props.modelValue))
  const groupOf = player => (['team', 'alumni'].includes(player.roster_category) ? player.roster_category : 'others')
  const groups = computed(() => {
    const term = keyword.value.trim().toLowerCase()
    const visible = props.players.filter(player => !term || player.name.toLowerCase().includes(term))
    return GROUPS.map(group => ({ ...group, players: visible.filter(player => groupOf(player) === group.key) })).filter(
      group => group.players.length
    )
  })

  const toggle = id => {
    const next = new Set(selected.value)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    emit('update:modelValue', [...next])
  }

  const selectTeam = () => {
    const team = props.players.filter(player => player.roster_category === 'team').map(player => player.id)
    emit('update:modelValue', [...new Set([...props.modelValue, ...team])])
  }
</script>

<style scoped>
  .toolbar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
  }
  .search {
    width: 180px;
  }
  .group {
    margin-bottom: 14px;
  }
  .group h3 {
    margin: 0 0 8px;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px 4px 4px;
    border: 1px solid var(--line);
    background: var(--surface-2);
    color: var(--ink-2);
    font: inherit;
    font-size: 15px;
    cursor: pointer;
    transition:
      background var(--duration-fast),
      border-color var(--duration-fast);
  }
  .chip.active {
    border-color: var(--ink);
    background: var(--ink);
    color: var(--bg);
  }
</style>
