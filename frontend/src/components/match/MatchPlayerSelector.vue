<!-- MatchPlayerSelector.vue - 完整只讀支持版本 -->
<template>
  <div class="match-player-selector" :class="{ 'readonly-mode': disabled }">
    <!-- 動態網球場視覺化 -->
    <div class="arena-container">
      <div :class="courtClasses" :data-changing="isChangingCourt">
        <!-- 時間控制器 -->
        <div
          v-if="modelValue.time_slot"
          :class="timeControllerClasses"
          :style="disabled ? 'pointer-events: none; opacity: 0.6;' : ''"
          @click="disabled ? null : toggleTimeSlot"
        >
          <span class="time-icon">{{ currentTimeSlot.icon }}</span>
        </div>

        <!-- 球員vs球員視覺化容器 -->
        <div class="team-vs-container">
          <!-- 隊伍 A -->
          <div class="team-section">
            <div class="team-card" :class="{ 'has-players': hasTeamAPlayers }">
              <div class="team-header">
                <h3 class="team-title">隊伍 A</h3>
              </div>

              <!-- 球員1 (後排) -->
              <div class="player-slot">
                <div class="position-label-fixed team-a-position">後排</div>
                <n-button
                  v-if="!modelValue.player1_id"
                  dashed
                  block
                  class="select-player-btn"
                  :disabled="disabled"
                  @click="openPlayerSelector('player1_id')"
                >
                  <template #icon>
                    <n-icon :component="AddIcon" />
                  </template>
                  <div class="btn-content">
                    <div>選擇球員</div>
                  </div>
                </n-button>
                <div
                  v-else
                  class="selected-player"
                  :class="{ 'readonly-player': disabled }"
                  @click="disabled ? null : openPlayerSelector('player1_id')"
                >
                  <div class="player-card-compact">
                    <n-avatar
                      :size="32"
                      :style="{
                        backgroundColor: getPlayerColor(modelValue.player1_id),
                        color: '#fff'
                      }"
                    >
                      {{ getPlayerInitial(getPlayerName(modelValue.player1_id)) }}
                    </n-avatar>
                    <div class="player-details">
                      <div class="player-name-compact">{{ getPlayerName(modelValue.player1_id) }}</div>
                      <div v-if="getPlayerOrganization(modelValue.player1_id)" class="player-org-compact">
                        {{ getPlayerOrganization(modelValue.player1_id) }}
                      </div>
                    </div>
                    <n-button
                      v-if="!disabled"
                      size="small"
                      quaternary
                      circle
                      class="remove-btn"
                      @click.stop="clearPlayer('player1_id')"
                    >
                      <n-icon :component="CloseIcon" />
                    </n-button>
                  </div>
                </div>
              </div>

              <!-- 球員2 (前排) - 僅雙打顯示 -->
              <div v-if="modelValue.match_type === 'doubles'" class="player-slot">
                <div class="position-label-fixed team-a-position">前排</div>
                <n-button
                  v-if="!modelValue.player2_id"
                  dashed
                  block
                  class="select-player-btn"
                  :disabled="disabled"
                  @click="openPlayerSelector('player2_id')"
                >
                  <template #icon>
                    <n-icon :component="AddIcon" />
                  </template>
                  <div class="btn-content">
                    <div>選擇球員</div>
                  </div>
                </n-button>
                <div
                  v-else
                  class="selected-player"
                  :class="{ 'readonly-player': disabled }"
                  @click="disabled ? null : openPlayerSelector('player2_id')"
                >
                  <div class="player-card-compact">
                    <n-avatar
                      :size="32"
                      :style="{
                        backgroundColor: getPlayerColor(modelValue.player2_id),
                        color: '#fff'
                      }"
                    >
                      {{ getPlayerInitial(getPlayerName(modelValue.player2_id)) }}
                    </n-avatar>
                    <div class="player-details">
                      <div class="player-name-compact">{{ getPlayerName(modelValue.player2_id) }}</div>
                      <div v-if="getPlayerOrganization(modelValue.player2_id)" class="player-org-compact">
                        {{ getPlayerOrganization(modelValue.player2_id) }}
                      </div>
                    </div>
                    <n-button
                      v-if="!disabled"
                      size="small"
                      quaternary
                      circle
                      class="remove-btn"
                      @click.stop="clearPlayer('player2_id')"
                    >
                      <n-icon :component="CloseIcon" />
                    </n-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 白色橡皮球 VS 區域 -->
          <div class="vs-section">
            <div class="tennis-ball">
              <div class="ball-core"></div>
            </div>
          </div>

          <!-- 隊伍 B -->
          <div class="team-section">
            <div class="team-card" :class="{ 'has-players': hasTeamBPlayers }">
              <div class="team-header">
                <h3 class="team-title">隊伍 B</h3>
              </div>

              <!-- 球員3 (後排) -->
              <div class="player-slot">
                <div class="position-label-fixed team-b-position">後排</div>
                <n-button
                  v-if="!modelValue.player3_id"
                  dashed
                  block
                  class="select-player-btn"
                  :disabled="disabled"
                  @click="openPlayerSelector('player3_id')"
                >
                  <template #icon>
                    <n-icon :component="AddIcon" />
                  </template>
                  <div class="btn-content">
                    <div>選擇球員</div>
                  </div>
                </n-button>
                <div
                  v-else
                  class="selected-player"
                  :class="{ 'readonly-player': disabled }"
                  @click="disabled ? null : openPlayerSelector('player3_id')"
                >
                  <div class="player-card-compact">
                    <n-avatar
                      :size="32"
                      :style="{
                        backgroundColor: getPlayerColor(modelValue.player3_id),
                        color: '#fff'
                      }"
                    >
                      {{ getPlayerInitial(getPlayerName(modelValue.player3_id)) }}
                    </n-avatar>
                    <div class="player-details">
                      <div class="player-name-compact">{{ getPlayerName(modelValue.player3_id) }}</div>
                      <div v-if="getPlayerOrganization(modelValue.player3_id)" class="player-org-compact">
                        {{ getPlayerOrganization(modelValue.player3_id) }}
                      </div>
                    </div>
                    <n-button
                      v-if="!disabled"
                      size="small"
                      quaternary
                      circle
                      class="remove-btn"
                      @click.stop="clearPlayer('player3_id')"
                    >
                      <n-icon :component="CloseIcon" />
                    </n-button>
                  </div>
                </div>
              </div>

              <!-- 球員4 (前排) - 僅雙打顯示 -->
              <div v-if="modelValue.match_type === 'doubles'" class="player-slot">
                <div class="position-label-fixed team-b-position">前排</div>
                <n-button
                  v-if="!modelValue.player4_id"
                  dashed
                  block
                  class="select-player-btn"
                  :disabled="disabled"
                  @click="openPlayerSelector('player4_id')"
                >
                  <template #icon>
                    <n-icon :component="AddIcon" />
                  </template>
                  <div class="btn-content">
                    <div>選擇球員</div>
                  </div>
                </n-button>
                <div
                  v-else
                  class="selected-player"
                  :class="{ 'readonly-player': disabled }"
                  @click="disabled ? null : openPlayerSelector('player4_id')"
                >
                  <div class="player-card-compact">
                    <n-avatar
                      :size="32"
                      :style="{
                        backgroundColor: getPlayerColor(modelValue.player4_id),
                        color: '#fff'
                      }"
                    >
                      {{ getPlayerInitial(getPlayerName(modelValue.player4_id)) }}
                    </n-avatar>
                    <div class="player-details">
                      <div class="player-name-compact">{{ getPlayerName(modelValue.player4_id) }}</div>
                      <div v-if="getPlayerOrganization(modelValue.player4_id)" class="player-org-compact">
                        {{ getPlayerOrganization(modelValue.player4_id) }}
                      </div>
                    </div>
                    <n-button
                      v-if="!disabled"
                      size="small"
                      quaternary
                      circle
                      class="remove-btn"
                      @click.stop="clearPlayer('player4_id')"
                    >
                      <n-icon :component="CloseIcon" />
                    </n-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 球員選擇模態框 - 完整訪客功能 -->
    <n-modal
      v-model:show="showPlayerSelector"
      preset="card"
      title="選擇球員"
      style="width: 90%; max-width: 800px"
      :mask-closable="false"
    >
      <div class="modal-content">
        <n-tabs v-model:value="playerSelectorTab" type="segment" style="margin-bottom: 1rem">
          <!-- 現有球員選擇 -->
          <n-tab-pane name="existing" tab="選擇現有球員">
            <n-input
              v-model:value="modalSearchTerm"
              placeholder="搜尋球員姓名或組織..."
              clearable
              style="margin-bottom: 1.5rem"
              size="large"
            >
              <template #prefix>
                <n-icon :component="SearchIcon" />
              </template>
            </n-input>

            <n-grid :x-gap="16" :y-gap="16" cols="1 s:2 m:3 l:4" responsive="screen">
              <n-grid-item
                v-for="player in filteredPlayersForModal"
                :key="player.id"
                @click="selectPlayerFromModal(player.id)"
              >
                <div
                  class="player-card"
                  :class="{
                    selected: isPlayerSelected(player.id),
                    disabled: isPlayerSelected(player.id),
                    guest: player.is_guest
                  }"
                >
                  <div class="player-card-inner">
                    <n-avatar
                      round
                      :style="{
                        backgroundColor: getPlayerColor(player.id),
                        color: '#fff'
                      }"
                      size="large"
                    >
                      {{ getPlayerInitial(player.name) }}
                    </n-avatar>
                    <div class="player-card-info">
                      <div class="player-card-name">
                        {{ player.name }}
                        <n-tag v-if="player.is_guest" size="tiny" type="warning" style="margin-left: 0.5rem">
                          訪客
                        </n-tag>
                      </div>
                      <div v-if="player.organization" class="player-card-org">
                        {{ player.organization.short_name || player.organization.name }}
                      </div>
                      <div v-else-if="player.is_guest && player.guest_phone" class="player-card-org">
                        {{ player.guest_phone }}
                      </div>
                    </div>
                    <!-- 已選中提示 -->
                    <div v-if="isPlayerSelected(player.id)" class="selected-overlay">
                      <n-icon :component="CheckIcon" size="24" />
                      <span>已選中</span>
                    </div>
                  </div>
                </div>
              </n-grid-item>
            </n-grid>
          </n-tab-pane>

          <!-- 創建新訪客 -->
          <n-tab-pane name="create-guest" tab="創建新訪客">
            <div class="modern-guest-form">
              <n-form ref="guestFormRef" :model="guestForm" :rules="guestRules" label-placement="top">
                <!-- 基本資訊 -->
                <div class="form-section">
                  <div class="section-header">
                    <h4 class="section-title">基本資訊</h4>
                    <p class="section-subtitle">填寫訪客的基本聯絡資訊</p>
                  </div>
                  <div class="form-grid">
                    <n-form-item label="訪客姓名" path="name" class="form-item-modern">
                      <n-input
                        v-model:value="guestForm.name"
                        placeholder="請輸入訪客姓名"
                        :maxlength="20"
                        show-count
                        size="large"
                        class="modern-input"
                      />
                    </n-form-item>

                    <n-form-item label="聯絡電話" path="phone" class="form-item-modern">
                      <n-input
                        v-model:value="guestForm.phone"
                        placeholder="選填"
                        :maxlength="15"
                        size="large"
                        class="modern-input"
                      />
                    </n-form-item>
                  </div>
                </div>

                <!-- 身份和歸屬 -->
                <div class="form-section">
                  <div class="section-header">
                    <h4 class="section-title">身份設定</h4>
                    <p class="section-subtitle">設定訪客在比賽中的身份與歸屬</p>
                  </div>
                  <div class="form-grid">
                    <n-form-item label="訪客身份" path="guest_role" class="form-item-modern">
                      <n-select
                        v-model:value="guestForm.guest_role"
                        :options="guestRoleOptions"
                        placeholder="選擇訪客在比賽中的身份"
                        size="large"
                        class="modern-select"
                      />
                    </n-form-item>

                    <n-form-item label="所屬組織" path="organization_id" class="form-item-modern">
                      <n-select
                        v-model:value="guestForm.organization_id"
                        :options="organizationOptions"
                        placeholder="選擇訪客所屬組織（可選）"
                        clearable
                        filterable
                        size="large"
                        class="modern-select"
                      />
                    </n-form-item>
                  </div>
                </div>

                <!-- 備註說明 -->
                <div class="form-section">
                  <div class="section-header">
                    <h4 class="section-title">備註說明</h4>
                    <p class="section-subtitle">添加額外的說明或記錄</p>
                  </div>
                  <n-form-item label="備註" path="notes" class="form-item-modern">
                    <n-input
                      v-model:value="guestForm.notes"
                      type="textarea"
                      placeholder="例如：來自XX學校、替補球員、首次合作等..."
                      :rows="4"
                      :maxlength="200"
                      show-count
                      size="large"
                      class="modern-textarea"
                    />
                  </n-form-item>
                </div>

                <!-- 操作按鈕 -->
                <div class="form-actions">
                  <n-button size="large" class="cancel-btn" @click="cancelGuestCreation"> 取消 </n-button>
                  <n-button
                    type="primary"
                    :loading="creatingGuest"
                    size="large"
                    class="create-btn"
                    @click="createAndSelectGuest"
                  >
                    <template #icon>
                      <n-icon :component="AddIcon" />
                    </template>
                    創建並選擇
                  </n-button>
                </div>
              </n-form>
            </div>
          </n-tab-pane>

          <!-- 我的訪客記錄 -->
          <n-tab-pane name="my-guests" tab="我的訪客">
            <div class="modern-guest-list">
              <div class="search-container">
                <n-input
                  v-model:value="myGuestsSearch"
                  placeholder="搜尋我創建的訪客..."
                  clearable
                  size="large"
                  class="modern-search"
                >
                  <template #prefix>
                    <n-icon :component="SearchIcon" />
                  </template>
                </n-input>
              </div>

              <n-spin :show="loadingMyGuests">
                <div v-if="filteredMyGuests.length > 0" class="guest-cards-container">
                  <div
                    v-for="guest in filteredMyGuests"
                    :key="guest.id"
                    class="modern-guest-card"
                    :class="{ selected: isPlayerSelected(guest.id) }"
                    @click="selectGuestFromHistory(guest.id)"
                  >
                    <div class="guest-avatar-section">
                      <n-avatar
                        round
                        :style="{ backgroundColor: getPlayerColor(guest.id), color: '#fff' }"
                        size="large"
                      >
                        {{ getPlayerInitial(guest.name) }}
                      </n-avatar>
                      <div v-if="isPlayerSelected(guest.id)" class="selected-badge">
                        <n-icon :component="CheckIcon" size="16" />
                      </div>
                    </div>

                    <div class="guest-info-section">
                      <div class="guest-header">
                        <h4 class="guest-name">{{ guest.name }}</h4>
                        <n-tag size="small" :type="getGuestRoleTagType(guest.guest_role)" class="role-tag">
                          {{ guest.guest_role_display || '中性' }}
                        </n-tag>
                      </div>

                      <div class="guest-details">
                        <div v-if="guest.organization" class="organization-info">
                          <span class="detail-icon">🏢</span>
                          {{ guest.organization.short_name || guest.organization.name }}
                        </div>
                        <div class="usage-info">
                          <span class="detail-icon">📊</span>
                          使用 {{ guest.usage_count || 0 }} 次
                        </div>
                        <div v-if="guest.last_used_at" class="last-used-info">
                          <span class="detail-icon">🕒</span>
                          最近：{{ formatDate(guest.last_used_at) }}
                        </div>
                      </div>

                      <div v-if="guest.guest_notes" class="guest-notes">
                        {{ guest.guest_notes }}
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="empty-state">
                  <div class="empty-icon">👥</div>
                  <h3>尚未創建任何訪客</h3>
                  <p>點擊「創建新訪客」分頁來添加第一個訪客</p>
                </div>
              </n-spin>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showPlayerSelector = false">取消</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref, watch, nextTick } from 'vue'
  import { useMessage } from 'naive-ui'
  import apiClient from '@/services/apiClient.js'

  // Icons
  import {
    AddOutline as AddIcon,
    CheckmarkOutline as CheckIcon,
    CloseOutline as CloseIcon,
    SearchOutline as SearchIcon
  } from '@vicons/ionicons5'

  // Props
  const props = defineProps({
    modelValue: {
      type: Object,
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    }
  })

  // Emits
  const emit = defineEmits(['update:modelValue', 'player-changed'])

  // State
  const message = useMessage()
  const showPlayerSelector = ref(false)
  const currentSelectingField = ref(null)
  const modalSearchTerm = ref('')
  const selectedOrganization = ref(null)
  const allActiveMembers = ref([])
  const organizationOptions = ref([])
  const isChangingCourt = ref(false)

  // 訪客功能相關狀態
  const myGuestsList = ref([])
  const playerSelectorTab = ref('existing')
  const myGuestsSearch = ref('')
  const loadingMyGuests = ref(false)
  const creatingGuest = ref(false)
  const guestRoleOptions = ref([])
  const guestForm = ref({
    name: '',
    phone: '',
    guest_role: 'neutral',
    organization_id: null,
    notes: ''
  })
  const guestFormRef = ref(null)

  // 訪客表單驗證規則
  const guestRules = {
    name: [
      { required: true, message: '請輸入訪客姓名', trigger: 'blur' },
      { min: 2, max: 20, message: '姓名長度應為2-20個字符', trigger: 'blur' }
    ],
    phone: [{ pattern: /^[0-9\-+\s()]*$/, message: '請輸入有效的電話號碼', trigger: 'blur' }],
    guest_role: [{ required: true, message: '請選擇訪客身份', trigger: 'change' }]
  }

  // Time slot config
  const timeSlotConfig = {
    morning: {
      label: '早上',
      icon: '🌅',
      next: 'afternoon'
    },
    afternoon: {
      label: '下午',
      icon: '☀️',
      next: 'evening'
    },
    evening: {
      label: '晚上',
      icon: '🌙',
      next: 'morning'
    }
  }

  // 計算屬性
  const hasTeamAPlayers = computed(() => {
    return props.modelValue.player1_id && (props.modelValue.match_type === 'singles' || props.modelValue.player2_id)
  })

  const hasTeamBPlayers = computed(() => {
    return props.modelValue.player3_id && (props.modelValue.match_type === 'singles' || props.modelValue.player4_id)
  })

  const currentTimeSlot = computed(() => {
    return timeSlotConfig[props.modelValue.time_slot] || timeSlotConfig.morning
  })

  const courtClasses = computed(() => {
    const classes = ['match-arena']

    if (props.modelValue.court_surface) {
      classes.push(`court-${props.modelValue.court_surface}`)
    }

    if (props.modelValue.time_slot) {
      classes.push(`time-${props.modelValue.time_slot}`)
    }

    if (props.modelValue.court_environment) {
      classes.push(`env-${props.modelValue.court_environment}`)
    }

    return classes
  })

  const timeControllerClasses = computed(() => {
    const classes = ['time-controller']
    if (props.modelValue.time_slot) {
      classes.push(props.modelValue.time_slot)
    }
    return classes
  })

  const filteredPlayersForModal = computed(() => {
    if (!modalSearchTerm.value) return allActiveMembers.value

    const searchTerm = modalSearchTerm.value.toLowerCase()

    return allActiveMembers.value.filter(player => {
      const playerName = (player.name || '').toLowerCase()
      const orgName = player.organization
        ? (player.organization.short_name || player.organization.name || '').toLowerCase()
        : ''

      return playerName.includes(searchTerm) || orgName.includes(searchTerm)
    })
  })

  const filteredMyGuests = computed(() => {
    if (!myGuestsSearch.value.trim()) {
      return myGuestsList.value
    }

    const searchTerm = myGuestsSearch.value.toLowerCase()
    return myGuestsList.value.filter(
      guest =>
        guest.name.toLowerCase().includes(searchTerm) ||
        (guest.organization?.name || '').toLowerCase().includes(searchTerm) ||
        (guest.guest_phone || '').includes(searchTerm) ||
        (guest.guest_notes || '').toLowerCase().includes(searchTerm)
    )
  })

  // Methods
  const updateData = (field, value) => {
    const updatedValue = {
      ...props.modelValue,
      [field]: value
    }

    emit('update:modelValue', updatedValue)

    if (field.includes('player') && field.includes('_id')) {
      emit('player-changed', { field, playerId: value, allPlayers: getAllSelectedPlayers() })
    }
  }

  const getAllSelectedPlayers = () => {
    return {
      player1_id: props.modelValue.player1_id,
      player2_id: props.modelValue.player2_id,
      player3_id: props.modelValue.player3_id,
      player4_id: props.modelValue.player4_id
    }
  }

  // 最強健的球員查找方法
  const findPlayerById = playerId => {
    if (!playerId) return null

    const playerIdStr = String(playerId)
    let foundPlayer = null

    for (const player of allActiveMembers.value) {
      if (String(player.id) === playerIdStr) {
        foundPlayer = player
        break
      }
    }

    if (!foundPlayer && playerId) {
      console.warn(`找不到球員 ID: ${playerId}`)
    }

    return foundPlayer
  }

  const getPlayerName = playerId => {
    const player = findPlayerById(playerId)
    return player?.name || '未知球員'
  }

  const getPlayerOrganization = playerId => {
    const player = findPlayerById(playerId)
    return player?.organization ? player.organization.short_name || player.organization.name : ''
  }

  const getPlayerInitial = name => {
    if (!name || name === '未知球員') return '?'
    return name.charAt(0).toUpperCase()
  }

  const getPlayerColor = playerId => {
    if (!playerId) return '#f0f0f0'
    const colors = ['#18a058', '#2080f0', '#f0a020', '#d03050', '#7c3aed', '#06b6d4', '#10b981', '#f59e0b']
    return colors[playerId % colors.length]
  }

  const getGuestRoleTagType = role => {
    const typeMap = {
      teammate: 'success',
      opponent: 'warning',
      substitute: 'info',
      neutral: 'default'
    }
    return typeMap[role] || 'default'
  }

  const isPlayerSelected = playerId => {
    if (!playerId) return false

    const playerIdStr = String(playerId)
    return (
      String(props.modelValue.player1_id) === playerIdStr ||
      String(props.modelValue.player2_id) === playerIdStr ||
      String(props.modelValue.player3_id) === playerIdStr ||
      String(props.modelValue.player4_id) === playerIdStr
    )
  }

  const clearPlayer = field => {
    // 🔧 添加 disabled 檢查
    if (props.disabled) {
      return
    }
    updateData(field, null)
  }

  const openPlayerSelector = field => {
    // 🔧 添加 disabled 檢查
    if (props.disabled) {
      return
    }
    currentSelectingField.value = field
    modalSearchTerm.value = ''
    showPlayerSelector.value = true
  }

  const selectPlayerFromModal = playerId => {
    if (isPlayerSelected(playerId)) {
      message.warning('此球員已被選中，請選擇其他球員')
      return
    }

    updateData(currentSelectingField.value, playerId)
    showPlayerSelector.value = false
    currentSelectingField.value = null
  }

  const toggleTimeSlot = () => {
    // 🔧 添加 disabled 檢查
    if (props.disabled) {
      return
    }
    const current = props.modelValue.time_slot
    const next = timeSlotConfig[current]?.next || 'morning'
    updateData('time_slot', next)
  }

  const triggerCourtAnimation = () => {
    isChangingCourt.value = true
    setTimeout(() => {
      isChangingCourt.value = false
    }, 600)
  }

  // 訪客相關方法
  const loadGuestRoleOptions = async () => {
    try {
      const response = await apiClient.get('/guests/role-options')
      guestRoleOptions.value = response.data.map(option => ({ value: option.value, label: option.label }))
    } catch (error) {
      console.error('載入訪客身份選項失敗:', error)
    }
  }

  const loadMyGuests = async () => {
    loadingMyGuests.value = true
    try {
      const response = await apiClient.get('/guests', {
        params: { limit: 50 }
      })
      myGuestsList.value = response.data
      syncGuestsToMainList()
    } catch (error) {
      console.error('載入我的訪客失敗:', error)
      message.error('載入訪客記錄失敗')
    } finally {
      loadingMyGuests.value = false
    }
  }

  const syncGuestsToMainList = () => {
    let addedCount = 0
    myGuestsList.value.forEach(guest => {
      const existsInMainList = allActiveMembers.value.some(p => String(p.id) === String(guest.id))
      if (!existsInMainList) {
        allActiveMembers.value.unshift(guest)
        addedCount++
      }
    })

    if (addedCount > 0) {
      console.log(`同步了 ${addedCount} 位訪客到主列表`)
    }
  }

  const createAndSelectGuest = async () => {
    try {
      await guestFormRef.value?.validate()
      creatingGuest.value = true

      const response = await apiClient.post('/guests', guestForm.value)
      const apiMember = response.data

      const newGuest = {
        id: apiMember.id,
        name: apiMember.name || guestForm.value.name,
        is_guest: true,
        organization: apiMember.organization || null,
        guest_phone: apiMember.guest_phone || guestForm.value.phone,
        guest_role: apiMember.guest_role || guestForm.value.guest_role,
        guest_notes: apiMember.guest_notes || guestForm.value.notes,
        usage_count: apiMember.usage_count || 0,
        last_used_at: apiMember.last_used_at || null,
        created_at: apiMember.created_at || new Date().toISOString(),
        mu: apiMember.mu || 25.0,
        sigma: apiMember.sigma || 8.333,
        display_name: apiMember.display_name || apiMember.name || guestForm.value.name,
        short_display_name: apiMember.short_display_name || apiMember.name || guestForm.value.name,
        student_id: apiMember.student_id || null,
        gender: apiMember.gender || null,
        position: apiMember.position || null,
        is_active: apiMember.is_active !== undefined ? apiMember.is_active : true,
        joined_date: apiMember.joined_date || null,
        leaved_date: apiMember.leaved_date || null,
        user: apiMember.user || null,
        racket: apiMember.racket || null,
        notes: apiMember.notes || null
      }

      allActiveMembers.value.unshift(newGuest)
      myGuestsList.value.unshift(newGuest)

      await nextTick()

      const verifyInMainList = allActiveMembers.value.some(p => String(p.id) === String(newGuest.id))

      if (!verifyInMainList) {
        console.warn('訪客未正確添加到主列表，重試添加')
        allActiveMembers.value = [newGuest, ...allActiveMembers.value]
      }

      if (currentSelectingField.value) {
        updateData(currentSelectingField.value, newGuest.id)
        await nextTick()

        const verifyName = getPlayerName(newGuest.id)
        if (verifyName === '未知球員') {
          console.error('訪客選擇失敗，嘗試同步修復')
          syncGuestsToMainList()
        }
      }

      resetGuestForm()
      showPlayerSelector.value = false
      currentSelectingField.value = null

      message.success(`訪客 "${newGuest.name}" 創建成功並已選擇！`)
    } catch (error) {
      console.error('創建訪客失敗:', error)
      const errorMessage = error.response?.data?.message || error.message || '創建訪客失敗'
      message.error(errorMessage)
    } finally {
      creatingGuest.value = false
    }
  }

  const selectGuestFromHistory = guestId => {
    if (isPlayerSelected(guestId)) {
      message.warning('此球員已被選中，請選擇其他球員')
      return
    }

    const guest = myGuestsList.value.find(g => String(g.id) === String(guestId))
    if (guest) {
      const existsInMainList = allActiveMembers.value.some(p => String(p.id) === String(guestId))
      if (!existsInMainList) {
        allActiveMembers.value.unshift(guest)
      }

      guest.usage_count = (guest.usage_count || 0) + 1
      guest.last_used_at = new Date().toISOString()
    }

    if (currentSelectingField.value) {
      updateData(currentSelectingField.value, guestId)
    }

    showPlayerSelector.value = false
    currentSelectingField.value = null
  }

  const cancelGuestCreation = () => {
    resetGuestForm()
    playerSelectorTab.value = 'existing'
  }

  const resetGuestForm = () => {
    guestForm.value = {
      name: '',
      phone: '',
      guest_role: 'neutral',
      organization_id: null,
      notes: ''
    }
  }

  const formatDate = dateString => {
    return new Date(dateString).toLocaleDateString('zh-TW')
  }

  const fetchActiveMembers = async () => {
    try {
      const response = await apiClient.get('/members', {
        params: {
          sort_by: 'name',
          sort_order: 'asc'
        }
      })

      const membersData = response.data

      allActiveMembers.value = membersData

      const organizations = new Set()
      membersData.forEach(member => {
        if (member.organization) {
          organizations.add(
            JSON.stringify({
              value: member.organization.id,
              label: member.organization.short_name || member.organization.name
            })
          )
        }
      })

      organizationOptions.value = [...Array.from(organizations).map(org => JSON.parse(org))].sort((a, b) =>
        a.label.localeCompare(b.label)
      )
    } catch (error) {
      console.error('獲取球員列表失敗:', error)
      message.error('獲取球員列表失敗。')
    }
  }

  const formatTimestampToDate = timestamp => {
    if (!timestamp) return null
    const date = new Date(timestamp)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }

  const syncDateFields = () => {
    if (props.modelValue.match_date_ts && !props.modelValue.match_date) {
      const dateString = formatTimestampToDate(props.modelValue.match_date_ts)
      updateData('match_date', dateString)
    }
  }

  const addPlayersToList = players => {
    if (!Array.isArray(players)) {
      console.warn('addPlayersToList: players 必須是陣列')
      return
    }

    players.forEach(player => {
      if (!player || !player.id) {
        console.warn('跳過無效球員:', player)
        return
      }

      const existsInMainList = allActiveMembers.value.some(p => String(p.id) === String(player.id))

      if (!existsInMainList) {
        const completePlayer = {
          id: player.id,
          name: player.name || '未知球員',
          is_guest: player.is_guest || false,
          organization: player.organization || null,
          guest_phone: player.guest_phone || null,
          guest_role: player.guest_role || null,
          guest_notes: player.guest_notes || null,
          usage_count: player.usage_count || 0,
          last_used_at: player.last_used_at || null,
          created_at: player.created_at || null,
          mu: player.mu || 25.0,
          sigma: player.sigma || 8.333,
          display_name: player.display_name || player.name,
          short_display_name: player.short_display_name || player.name,
          student_id: player.student_id || null,
          gender: player.gender || null,
          position: player.position || null,
          is_active: player.is_active !== undefined ? player.is_active : true,
          joined_date: player.joined_date || null,
          leaved_date: player.leaved_date || null,
          user: player.user || null,
          racket: player.racket || null,
          notes: player.notes || null
        }

        allActiveMembers.value.unshift(completePlayer)
        // console.log(`添加球員到列表: ${completePlayer.name} (ID: ${completePlayer.id})`)

        if (completePlayer.is_guest) {
          const existsInGuestList = myGuestsList.value.some(g => String(g.id) === String(completePlayer.id))
          if (!existsInGuestList) {
            myGuestsList.value.unshift(completePlayer)
          }
        }
      }
    })

    // console.log(`當前球員列表大小: ${allActiveMembers.value.length}`)
  }

  // 暴露方法給父組件使用
  defineExpose({
    addPlayersToList,
    getPlayerName,
    getPlayerOrganization,
    getAllSelectedPlayers,
    getTeamDisplayName: side => {
      if (side === 'A') {
        const player1 = getPlayerName(props.modelValue.player1_id)
        const player2 = props.modelValue.match_type === 'doubles' ? getPlayerName(props.modelValue.player2_id) : ''
        return player2 && player2 !== '未知球員' ? `${player1} / ${player2}` : player1
      } else {
        const player3 = getPlayerName(props.modelValue.player3_id)
        const player4 = props.modelValue.match_type === 'doubles' ? getPlayerName(props.modelValue.player4_id) : ''
        return player4 && player4 !== '未知球員' ? `${player3} / ${player4}` : player3
      }
    }
  })

  // Watchers
  watch(
    [() => props.modelValue.court_surface, () => props.modelValue.court_environment, () => props.modelValue.time_slot],
    () => {
      triggerCourtAnimation()
    }
  )

  watch(showPlayerSelector, async show => {
    if (show) {
      await loadMyGuests()
      await loadGuestRoleOptions()
      syncGuestsToMainList()
    }
  })

  watch(showPlayerSelector, show => {
    if (!show) {
      playerSelectorTab.value = 'existing'
    }
  })

  watch(
    () => props.modelValue.match_date_ts,
    newTimestamp => {
      if (newTimestamp && !props.modelValue.match_date) {
        const dateString = formatTimestampToDate(newTimestamp)
        updateData('match_date', dateString)
      }
    },
    { immediate: true }
  )

  watch(
    [
      () => props.modelValue.player1_id,
      () => props.modelValue.player2_id,
      () => props.modelValue.player3_id,
      () => props.modelValue.player4_id
    ],
    async (newPlayerIds, oldPlayerIds) => {
      const newIds = newPlayerIds.filter((id, index) => id !== oldPlayerIds?.[index] && id !== null)

      if (newIds.length > 0) {
        await loadMatchPlayers(newIds)
      }
    },
    { deep: true }
  )

  // Lifecycle
  onMounted(async () => {
    await fetchActiveMembers()
    syncDateFields()

    setTimeout(() => {
      syncGuestsToMainList()
    }, 1000)
  })

  const loadMatchPlayers = async playerIds => {
    try {
      const validPlayerIds = playerIds.filter(id => id !== null && id !== undefined)

      if (validPlayerIds.length === 0) {
        return
      }

      // console.log('載入比賽相關球員:', validPlayerIds)

      const playerPromises = validPlayerIds.map(async playerId => {
        try {
          const response = await apiClient.get(`/members/${playerId}`)
          return response.data
        } catch (error) {
          console.warn(`無法載入球員 ${playerId}:`, error)
          return null
        }
      })

      const players = await Promise.all(playerPromises)
      const validPlayers = players.filter(player => player !== null)

      if (validPlayers.length > 0) {
        addPlayersToList(validPlayers)
      }
    } catch (error) {
      console.error('載入比賽球員失敗:', error)
    }
  }
</script>

<style scoped>
  @import '@/assets/css/components/match/match-player-selector.css';

  /* 🔧 只讀模式樣式 */
  .match-player-selector.readonly-mode {
    opacity: 0.8;
    pointer-events: auto; /* 保持基本的滾動和查看功能 */
  }

  .readonly-player {
    cursor: default !important;
    pointer-events: none;
  }

  .readonly-mode .select-player-btn[disabled] {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }

  .readonly-mode .remove-btn {
    display: none; /* 只讀模式下隱藏移除按鈕 */
  }

  /* 禁用狀態的視覺反饋 */
  .readonly-mode .player-card-compact {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 0.75rem;
  }

  .readonly-mode .selected-player:hover {
    transform: none; /* 禁用懸停動畫 */
  }

  /* 模態框樣式優化 */
  .modal-content {
    padding: 0;
  }

  /* 現代化訪客表單樣式 */
  .modern-guest-form {
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
  }

  .form-section {
    margin-bottom: 2rem;
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    border: 1px solid #e2e8f0;
  }

  .section-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e2e8f0;
  }

  .section-title {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a202c;
  }

  .section-subtitle {
    margin: 0;
    font-size: 0.875rem;
    color: #64748b;
    line-height: 1.5;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  @media (max-width: 768px) {
    .form-grid {
      grid-template-columns: 1fr;
    }
  }

  .form-item-modern {
    margin-bottom: 0;
  }

  .modern-input,
  .modern-select,
  .modern-textarea {
    border-radius: 12px;
    transition: all 0.3s ease;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
  }

  .cancel-btn {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #64748b;
    border-radius: 12px;
  }

  .create-btn {
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }

  .create-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }

  /* 現代化訪客列表樣式 */
  .modern-guest-list {
    padding: 1rem;
  }

  .search-container {
    margin-bottom: 1.5rem;
  }

  .modern-search {
    border-radius: 12px;
    background: white;
    border: 1px solid #e2e8f0;
  }

  .guest-cards-container {
    display: grid;
    gap: 1rem;
    max-height: 500px;
    overflow-y: auto;
    padding: 0.5rem;
  }

  .modern-guest-card {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.25rem;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
  }

  .modern-guest-card:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  }

  .modern-guest-card.selected {
    border-color: #10b981;
    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
  }

  .guest-avatar-section {
    position: relative;
    flex-shrink: 0;
  }

  .selected-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 24px;
    height: 24px;
    background: #10b981;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    border: 2px solid white;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  }

  .guest-info-section {
    flex: 1;
    min-width: 0;
  }

  .guest-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .guest-name {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: #1a202c;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .role-tag {
    border-radius: 8px;
    font-weight: 500;
  }

  .guest-details {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .organization-info,
  .usage-info,
  .last-used-info {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.875rem;
    color: #64748b;
    background: #f8fafc;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
  }

  .detail-icon {
    font-size: 0.75rem;
  }

  .guest-notes {
    font-size: 0.875rem;
    color: #64748b;
    background: #f8fafc;
    padding: 0.75rem;
    border-radius: 8px;
    border-left: 3px solid #667eea;
    line-height: 1.5;
  }

  /* 空狀態樣式 */
  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #64748b;
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .empty-state h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #374151;
  }

  .empty-state p {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  /* 統一隊伍標籤顏色 */
  .position-label-fixed.team-a-position {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }

  .position-label-fixed.team-b-position {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
  }

  /* 獲勝隊伍高亮效果 - 只保留邊框發亮 */
  .team-card.winner-glow {
    border-color: #10b981 !important;
    box-shadow:
      0 0 0 3px rgba(16, 185, 129, 0.3),
      0 0 20px rgba(16, 185, 129, 0.4),
      0 10px 30px rgba(0, 0, 0, 0.2) !important;
    animation: winner-glow-pulse 2s ease-in-out infinite;
  }

  @keyframes winner-glow-pulse {
    0%,
    100% {
      box-shadow:
        0 0 0 3px rgba(16, 185, 129, 0.3),
        0 0 20px rgba(16, 185, 129, 0.4),
        0 10px 30px rgba(0, 0, 0, 0.2);
    }
    50% {
      box-shadow:
        0 0 0 5px rgba(16, 185, 129, 0.5),
        0 0 30px rgba(16, 185, 129, 0.6),
        0 15px 40px rgba(0, 0, 0, 0.25);
    }
  }

  /* 球員卡片點擊區域優化 */
  .selected-player {
    cursor: pointer;
    transition: transform 0.2s ease;
  }

  .selected-player:hover {
    transform: scale(1.02);
  }

  .player-card-compact {
    position: relative;
    overflow: visible;
  }

  /* 球員選擇卡片增加 padding */
  .player-card {
    padding: 0;
    border-radius: 16px;
    overflow: hidden;
  }

  .player-card-inner {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    height: 100%;
  }

  .player-card.guest {
    border-left: 4px solid #f59e0b;
  }

  /* 響應式優化 */
  @media (max-width: 768px) {
    .modern-guest-form {
      padding: 1rem;
    }

    .form-section {
      padding: 1rem;
    }

    .guest-details {
      flex-direction: column;
      gap: 0.5rem;
    }

    .guest-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }
  }

  @media (max-width: 480px) {
    .player-card-inner {
      padding: 0.8rem;
    }

    .position-label-fixed.team-a-position,
    .position-label-fixed.team-b-position {
      padding: 0.25rem 0.5rem;
      font-size: 0.65rem;
    }
  }
</style>
