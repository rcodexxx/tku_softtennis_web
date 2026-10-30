<template>
  <n-modal
    :show="show"
    preset="card"
    title="選擇球員"
    style="width: min(760px, 96vw)"
    :mask-closable="true"
    @update:show="value => emit('update:show', value)"
  >
    <n-tabs v-model:value="tab" type="segment" animated>
      <n-tab-pane name="existing" tab="球員">
        <n-input v-model:value="searchTerm" placeholder="搜尋姓名或組織" clearable round class="search">
          <template #prefix><n-icon :component="SearchIcon" /></template>
        </n-input>
        <div class="player-grid">
          <button
            v-for="player in filteredPlayers"
            :key="player.id"
            type="button"
            class="player-tile"
            :class="{ selected: isPlayerSelected(player.id) }"
            @click="choose(player)"
          >
            <PlayerAvatar :id="player.id" :name="player.name" :src="player.avatar_url" :size="44" />
            <span class="tile-text">
              <span class="tile-name">
                {{ player.name }}
                <span v-if="player.is_guest" class="guest-tag">訪客</span>
              </span>
              <span class="tile-sub">{{ organizationLabel(player) || player.guest_phone || '—' }}</span>
            </span>
            <n-icon v-if="isPlayerSelected(player.id)" :component="CheckIcon" class="check" />
          </button>
        </div>
        <n-empty v-if="!filteredPlayers.length" description="找不到符合的球員" class="empty" />
      </n-tab-pane>

      <n-tab-pane name="my-guests" tab="我的訪客">
        <n-input v-model:value="myGuestsSearch" placeholder="搜尋我建立的訪客" clearable round class="search">
          <template #prefix><n-icon :component="SearchIcon" /></template>
        </n-input>
        <n-spin :show="loadingMyGuests">
          <div v-if="filteredMyGuests.length" class="guest-list">
            <button
              v-for="guest in filteredMyGuests"
              :key="guest.id"
              type="button"
              class="guest-row"
              :class="{ selected: isPlayerSelected(guest.id) }"
              @click="choose(guest)"
            >
              <PlayerAvatar :id="guest.id" :name="guest.name" :src="guest.avatar_url" :size="40" />
              <span class="guest-text">
                <span class="tile-name">
                  {{ guest.name }}
                  <n-tag size="small" round :type="getGuestRoleTagType(guest.guest_role)">
                    {{ guest.guest_role_label || '訪客' }}
                  </n-tag>
                </span>
                <span class="tile-sub">
                  {{ organizationLabel(guest) || '無組織' }} · 出賽 {{ guest.usage_count || 0 }} 次
                  <template v-if="guest.last_used_at">
                    · 最近 {{ new Date(guest.last_used_at).toLocaleDateString('zh-TW') }}
                  </template>
                </span>
                <span v-if="guest.guest_notes" class="guest-notes">{{ guest.guest_notes }}</span>
              </span>
              <n-icon v-if="isPlayerSelected(guest.id)" :component="CheckIcon" class="check" />
            </button>
          </div>
          <n-empty v-else description="還沒有建立過訪客" class="empty">
            <template #extra>
              <n-button size="small" @click="tab = 'create-guest'">新增訪客</n-button>
            </template>
          </n-empty>
        </n-spin>
      </n-tab-pane>

      <n-tab-pane name="create-guest" tab="新增訪客">
        <n-form ref="guestFormRef" :model="guestForm" :rules="guestRules" label-placement="top">
          <n-grid :cols="2" :x-gap="12" responsive="screen" item-responsive>
            <n-form-item-gi span="2 m:1" label="姓名" path="name">
              <n-input v-model:value="guestForm.name" placeholder="訪客姓名" :maxlength="20" show-count />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="電話" path="phone">
              <n-input v-model:value="guestForm.phone" placeholder="選填" :maxlength="15" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="身份" path="guest_role">
              <n-select v-model:value="guestForm.guest_role" :options="guestRoleOptions" />
            </n-form-item-gi>
            <n-form-item-gi span="2 m:1" label="所屬組織" path="organization_id">
              <n-select
                v-model:value="guestForm.organization_id"
                :options="organizationOptions"
                placeholder="選填"
                clearable
                filterable
              />
            </n-form-item-gi>
            <n-form-item-gi span="2" label="備註" path="notes">
              <n-input
                v-model:value="guestForm.notes"
                type="textarea"
                placeholder="例如：來自 XX 學校、替補球員"
                :rows="2"
                :maxlength="200"
                show-count
              />
            </n-form-item-gi>
          </n-grid>
          <div class="form-actions">
            <n-button @click="cancelGuestCreation">取消</n-button>
            <n-button type="primary" :loading="creatingGuest" @click="createAndSelectGuest">
              <template #icon><n-icon :component="AddIcon" /></template>
              建立並選擇
            </n-button>
          </div>
        </n-form>
      </n-tab-pane>
    </n-tabs>
  </n-modal>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { useMessage } from 'naive-ui'
  import { Add as AddIcon, Checkmark as CheckIcon, Search as SearchIcon } from '@vicons/carbon'
  import { guestsApi } from '@/api'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { organizationLabel } from '@/utils/player'

  /** 選擇球員的視窗：從現有球員挑選、建立新訪客，或從自己建立過的訪客挑選。 */
  const props = defineProps({
    show: { type: Boolean, default: false },
    players: { type: Array, default: () => [] },
    selectedIds: { type: Array, default: () => [] }
  })

  const emit = defineEmits(['update:show', 'select'])

  const message = useMessage()
  const tab = ref('existing')
  const searchTerm = ref('')
  const myGuestsSearch = ref('')
  const myGuests = ref([])
  const loadingMyGuests = ref(false)
  const guestRoleOptions = ref([])
  const creatingGuest = ref(false)
  const guestFormRef = ref(null)
  const guestForm = ref(emptyGuestForm())

  const guestRules = {
    name: [
      { required: true, message: '請輸入訪客姓名', trigger: 'blur' },
      { min: 2, max: 20, message: '姓名長度應為2-20個字符', trigger: 'blur' }
    ],
    phone: [{ pattern: /^[0-9\-+\s()]*$/, message: '請輸入有效的電話號碼', trigger: 'blur' }],
    guest_role: [{ required: true, message: '請選擇訪客身份', trigger: 'change' }]
  }

  function emptyGuestForm() {
    return { name: '', phone: '', guest_role: 'neutral', organization_id: null, notes: '' }
  }

  const isPlayerSelected = playerId => props.selectedIds.some(id => id && String(id) === String(playerId))

  /** 現有球員 + 自己建立、但不在球員列表裡的訪客（排在最前面）。 */
  const candidates = computed(() => {
    const known = new Set(props.players.map(p => String(p.id)))
    const extraGuests = myGuests.value.filter(g => !known.has(String(g.id))).reverse()
    return [...extraGuests, ...props.players]
  })

  const filteredPlayers = computed(() => {
    const term = searchTerm.value.toLowerCase()
    if (!term) return candidates.value
    return candidates.value.filter(player => {
      const org = player.organization ? player.organization.short_name || player.organization.name || '' : ''
      return (player.name || '').toLowerCase().includes(term) || org.toLowerCase().includes(term)
    })
  })

  const filteredMyGuests = computed(() => {
    const term = myGuestsSearch.value.trim().toLowerCase()
    if (!term) return myGuests.value
    return myGuests.value.filter(
      guest =>
        guest.name.toLowerCase().includes(term) ||
        (guest.organization?.name || '').toLowerCase().includes(term) ||
        (guest.guest_phone || '').includes(term) ||
        (guest.guest_notes || '').toLowerCase().includes(term)
    )
  })

  const organizationOptions = computed(() => {
    const options = new Map()
    for (const player of props.players) {
      if (player.organization) {
        const { id, short_name: shortName, name } = player.organization
        options.set(id, { value: id, label: shortName || name })
      }
    }
    return [...options.values()].sort((a, b) => a.label.localeCompare(b.label))
  })

  const getGuestRoleTagType = role => ({ teammate: 'success', opponent: 'warning' })[role] || 'default'

  const close = () => emit('update:show', false)

  const choose = player => {
    if (isPlayerSelected(player.id)) {
      message.warning('此球員已被選中，請選擇其他球員')
      return
    }
    emit('select', player)
    close()
  }

  const createAndSelectGuest = async () => {
    try {
      await guestFormRef.value?.validate()
    } catch {
      return
    }
    creatingGuest.value = true
    try {
      const guest = await guestsApi.create(guestForm.value)
      myGuests.value.unshift(guest)
      guestForm.value = emptyGuestForm()
      emit('select', guest)
      close()
      message.success(`訪客 "${guest.name}" 創建成功並已選擇！`)
    } catch (error) {
      message.error(error.response?.data?.message || '創建訪客失敗')
    } finally {
      creatingGuest.value = false
    }
  }

  const cancelGuestCreation = () => {
    guestForm.value = emptyGuestForm()
    tab.value = 'existing'
  }

  const loadGuests = async () => {
    loadingMyGuests.value = true
    try {
      myGuests.value = await guestsApi.search({ limit: 50 })
    } catch {
      message.error('載入訪客記錄失敗')
    } finally {
      loadingMyGuests.value = false
    }
  }

  watch(
    () => props.show,
    async show => {
      if (!show) {
        tab.value = 'existing'
        return
      }
      searchTerm.value = ''
      await loadGuests()
      if (!guestRoleOptions.value.length) {
        guestRoleOptions.value = await guestsApi.roleOptions().catch(() => [])
      }
    }
  )
</script>

<style scoped>
  .search {
    margin: 14px 0;
  }
  .player-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: 10px;
    max-height: 52vh;
    overflow-y: auto;
    padding: 2px;
  }
  .player-tile,
  .guest-row {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    text-align: left;
    cursor: pointer;
    font: inherit;
    color: inherit;
    transition:
      border-color var(--duration-fast),
      transform var(--duration-fast),
      box-shadow var(--duration-fast);
  }
  .player-tile:hover,
  .guest-row:hover {
    border-color: var(--blue-400);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }
  .selected {
    border-color: var(--blue-600);
    background: var(--blue-50);
    cursor: not-allowed;
  }
  .tile-text,
  .guest-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
    flex: 1;
  }
  .tile-name {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 700;
    color: var(--blue-900);
  }
  .tile-sub {
    font-size: 14px;
    color: var(--color-text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .guest-tag {
    padding: 0 6px;
    border-radius: var(--radius-full);
    background: var(--gold-100);
    color: var(--accent-text);
    font-size: 13px;
    font-weight: 600;
  }
  .check {
    color: var(--blue-600);
    font-size: 20px;
  }
  .guest-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 52vh;
    overflow-y: auto;
    padding: 2px;
  }
  .guest-notes {
    margin-top: 2px;
    font-size: 14px;
    color: var(--gray-700);
  }
  .empty {
    padding: 32px 0;
  }
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 8px;
  }
</style>
