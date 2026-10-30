<template>
  <div class="teams">
    <section v-for="team in teams" :key="team.key" class="team" :class="team.key">
      <h3 class="team-title">{{ team.title }}</h3>
      <template v-for="slot in team.slots" :key="slot.field">
        <div v-if="slot.visible" class="slot">
          <span class="position">{{ slot.position }}</span>
          <button
            v-if="!modelValue[slot.field]"
            type="button"
            class="pick"
            :disabled="disabled"
            @click="open(slot.field)"
          >
            <n-icon :component="Add" />
            選擇球員
          </button>
          <div v-else class="picked" :class="{ disabled }" @click="open(slot.field)">
            <PlayerAvatar
              :id="modelValue[slot.field]"
              :name="playerOf(slot.field)?.name || '?'"
              :src="playerOf(slot.field)?.avatar_url"
              :size="40"
            />
            <span class="picked-text">
              <span class="picked-name">{{ playerOf(slot.field)?.name || '載入中…' }}</span>
              <span class="picked-sub">{{
                organizationLabel(playerOf(slot.field)) || (playerOf(slot.field)?.is_guest ? '訪客' : '')
              }}</span>
            </span>
            <n-button v-if="!disabled" quaternary circle size="small" @click.stop="setPlayers({ [slot.field]: null })">
              <template #icon><n-icon :component="Close" /></template>
            </n-button>
          </div>
        </div>
      </template>
    </section>

    <button v-if="!disabled" type="button" class="swap" title="交換兩隊" @click="swapTeams">
      <n-icon :component="ArrowsHorizontal" size="20" />
    </button>

    <PlayerPickerModal
      v-model:show="pickerOpen"
      :players="members"
      :selected-ids="selectedIds"
      @select="handleChosen"
    />
  </div>
</template>

<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useMessage } from 'naive-ui'
  import { Add, ArrowsHorizontal, Close } from '@vicons/carbon'
  import { membersApi } from '@/api'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { organizationLabel } from '@/utils/player'
  import PlayerPickerModal from './PlayerPickerModal.vue'

  /** 兩隊球員的選擇。modelValue 需有 match_type 與 player1_id ~ player4_id，修改時回傳新物件。 */
  const props = defineProps({
    modelValue: { type: Object, required: true },
    disabled: { type: Boolean, default: false }
  })
  const emit = defineEmits(['update:modelValue'])

  const FIELDS = ['player1_id', 'player2_id', 'player3_id', 'player4_id']

  const message = useMessage()
  const members = ref([])
  const pickerOpen = ref(false)
  const selectingField = ref(null)

  const singles = computed(() => props.modelValue.match_type === 'singles')
  const selectedIds = computed(() => FIELDS.map(field => props.modelValue[field]))
  const teams = computed(() =>
    [
      { key: 'a', title: '隊伍 A', back: 'player1_id', front: 'player2_id' },
      { key: 'b', title: '隊伍 B', back: 'player3_id', front: 'player4_id' }
    ].map(team => ({
      ...team,
      slots: [
        { field: team.back, position: singles.value ? '球員' : '後排', visible: true },
        { field: team.front, position: '前排', visible: !singles.value }
      ]
    }))
  )

  const playerOf = field => members.value.find(p => p.id === props.modelValue[field])

  const setPlayers = changes => emit('update:modelValue', { ...props.modelValue, ...changes })

  const open = field => {
    if (props.disabled) return
    selectingField.value = field
    pickerOpen.value = true
  }

  const addMembers = players => {
    const known = new Set(members.value.map(p => p.id))
    members.value.push(...players.filter(p => !known.has(p.id)))
  }

  const handleChosen = player => {
    addMembers([player])
    setPlayers({ [selectingField.value]: player.id })
  }

  const swapTeams = () => {
    const f = props.modelValue
    setPlayers({
      player1_id: f.player3_id,
      player2_id: f.player4_id,
      player3_id: f.player1_id,
      player4_id: f.player2_id
    })
  }

  /** 已選的球員不在列表裡時（例如訪客、已離隊成員）個別載入。 */
  const loadMissing = async ids => {
    const missing = ids.filter(id => id && !members.value.some(p => p.id === id))
    addMembers((await Promise.all(missing.map(id => membersApi.get(id).catch(() => null)))).filter(Boolean))
  }

  watch(selectedIds, loadMissing)

  onMounted(async () => {
    try {
      members.value = await membersApi.list({ sort_by: 'name', sort_order: 'asc' })
    } catch {
      message.error('載入球員列表失敗')
    }
    loadMissing(selectedIds.value)
  })
</script>

<style scoped>
  .teams {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  .team {
    padding: 16px;
    border-radius: var(--radius-lg);
    border: 2px solid;
  }
  .team.a {
    border-color: var(--blue-200);
    background: var(--blue-50);
  }
  .team.b {
    border-color: #f9c4c6;
    background: #fff5f5;
  }
  .team-title {
    margin: 0 0 12px;
    font-size: 16px;
    font-weight: 800;
  }
  .a .team-title {
    color: var(--blue-700);
  }
  .b .team-title {
    color: var(--red-600);
  }
  .slot + .slot {
    margin-top: 10px;
  }
  .position {
    display: block;
    margin-bottom: 4px;
    font-size: 12px;
    font-weight: 700;
    color: var(--color-text-muted);
  }
  .pick {
    width: 100%;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius-md);
    background: color-mix(in srgb, var(--surface) 70%, transparent);
    color: var(--gray-500);
    font: inherit;
    font-weight: 700;
    cursor: pointer;
    transition:
      border-color var(--duration-fast),
      color var(--duration-fast);
  }
  .pick:hover:not(:disabled) {
    border-color: var(--blue-500);
    color: var(--blue-600);
  }
  .picked {
    display: flex;
    align-items: center;
    gap: 10px;
    height: 60px;
    padding: 0 10px;
    border-radius: var(--radius-md);
    background: var(--color-surface);
    box-shadow: var(--shadow-sm);
    cursor: pointer;
    animation: stagger-in var(--duration-base) var(--ease-out) both;
  }
  .picked.disabled {
    cursor: default;
  }
  .picked-text {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .picked-name {
    font-weight: 700;
    color: var(--blue-900);
  }
  .picked-sub {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .swap {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border: 3px solid var(--color-bg);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-surface);
    color: var(--blue-700);
    box-shadow: var(--shadow-md);
    cursor: pointer;
    transition: transform var(--duration-base) var(--ease-spring);
  }
  .swap:hover {
    transform: translate(-50%, -50%) rotate(180deg);
  }
  @media (max-width: 640px) {
    .teams {
      grid-template-columns: 1fr;
      gap: 28px;
    }
    .swap {
      transform: translate(-50%, -50%) rotate(90deg);
    }
  }
</style>
