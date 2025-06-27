// src/composables/useOptions.js
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/services/apiClient'

/**
 * 統一選項管理 Composable
 * 管理應用中所有的下拉選單選項，避免重複定義
 */
export function useOptions() {
  const message = useMessage()

  // ========== 靜態選項 ==========

  // 角色選項
  const roleOptions = [
    { label: '隊員', value: 'member' },
    { label: '幹部', value: 'cadre' },
    { label: '教練', value: 'coach' },
    { label: '管理員', value: 'admin' },
    { label: '訪客', value: 'guest' }
  ]

  // 性別選項
  const genderOptions = [
    { label: '男性', value: 'male' },
    { label: '女性', value: 'female' }
  ]

  // 位置選項
  const positionOptions = [
    { label: '後排', value: 'back' },
    { label: '前排', value: 'front' },
    { label: '皆可', value: 'versatile' }
  ]

  // 經驗等級選項
  const experienceLevelOptions = [
    { label: '新手', value: 'newcomer', icon: '🌱' },
    { label: '初學者', value: 'beginner', icon: '🌿' },
    { label: '初級', value: 'elementary', icon: '🌳' },
    { label: '中級下', value: 'intermediate_low', icon: '🎯' },
    { label: '中級', value: 'intermediate', icon: '⚡' },
    { label: '中級上', value: 'intermediate_high', icon: '🔥' },
    { label: '高級', value: 'advanced', icon: '💫' },
    { label: '專家級', value: 'expert', icon: '⭐' },
    { label: '職業級', value: 'professional', icon: '👑' }
  ]

  // 比賽類型選項
  const matchTypeOptions = [
    { label: '雙打', value: 'doubles' },
    { label: '單打', value: 'singles' }
  ]

  // 比賽格式選項
  const matchFormatOptions = [
    { label: '五局制', value: 'games_5' },
    { label: '七局制', value: 'games_7' },
    { label: '九局制', value: 'games_9' }
  ]

  // 勝負選項
  const winLossOptions = [
    { label: '勝利', value: 'win' },
    { label: '失敗', value: 'loss' }
  ]

  // 場地表面選項
  const courtSurfaceOptions = [
    { label: '硬地球場', value: 'hard_court' },
    { label: '紅土球場', value: 'clay_court' },
    { label: '草地球場', value: 'grass_court' }
  ]

  // 場地環境選項
  const courtEnvironmentOptions = [
    { label: '室外', value: 'outdoor' },
    { label: '室內', value: 'indoor' }
  ]

  // 時段配置
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

  // 時段選項 (從配置自動生成)
  const timeSlotOptions = Object.entries(timeSlotConfig).map(([value, config]) => ({
    label: config.label,
    value,
    icon: config.icon
  }))

  // 帶圖標的時段選項
  const timeSlotOptionsWithIcon = Object.entries(timeSlotConfig).map(([value, config]) => ({
    label: `${config.icon} ${config.label}`,
    value,
    icon: config.icon
  }))

  // ========== 動態選項 (需要 API 調用) ==========

  // 組織選項
  const organizationOptions = ref([])
  const organizationLoading = ref(false)

  const loadOrganizationOptions = async () => {
    if (organizationOptions.value.length > 0) return organizationOptions.value

    organizationLoading.value = true
    try {
      const response = await apiClient.get('/organizations')
      const organizations = Array.isArray(response.data) ? response.data : []
      organizationOptions.value = organizations.map(org => ({
        label: org.name,
        value: org.id
      }))
      return organizationOptions.value
    } catch (error) {
      message.error('載入組織列表失敗')
      return []
    } finally {
      organizationLoading.value = false
    }
  }

  // 球員選項
  const playerOptions = ref([])
  const playerLoading = ref(false)

  const loadPlayerOptions = async () => {
    if (playerOptions.value.length > 0) return playerOptions.value

    playerLoading.value = true
    try {
      const response = await apiClient.get('/members?all=true&sort_by=name&sort_order=asc')

      let membersData = response.data
      if (response.data?.members) membersData = response.data.members
      else if (response.data?.data) membersData = response.data.data

      if (!Array.isArray(membersData)) membersData = []

      playerOptions.value = membersData.map(member => ({
        label: member.name || member.display_name || `成員 ${member.id}`,
        value: member.id
      }))

      return playerOptions.value
    } catch (error) {
      message.error('載入球員列表失敗')
      return []
    } finally {
      playerLoading.value = false
    }
  }

  // ========== 輔助函數 ==========

  // 根據值獲取標籤
  const getOptionLabel = (options, value) => {
    const option = options.find(opt => opt.value === value)
    return option ? option.label : value
  }

  // 檢查值是否有效
  const isValidOption = (options, value) => {
    return options.some(opt => opt.value === value)
  }

  // 經驗等級相關函數 (你原本想要的功能)
  const getExperienceIcon = experienceLevel => {
    const option = experienceLevelOptions.find(opt => opt.value === experienceLevel)
    return option ? option.icon : '🌱'
  }

  const getExperienceLevelDisplay = experienceLevel => {
    return getOptionLabel(experienceLevelOptions, experienceLevel)
  }

  const getExperienceWithIcon = experienceLevel => {
    const option = experienceLevelOptions.find(opt => opt.value === experienceLevel)
    if (!option) return '🌱 新手'
    return `${option.icon} ${option.label}`
  }

  // 角色相關函數
  const getRoleDisplay = roleValue => {
    return getOptionLabel(roleOptions, roleValue)
  }

  const getRoleColor = roleValue => {
    const colors = {
      admin: 'error',
      cadre: 'warning',
      coach: 'success',
      member: 'info',
      guest: 'warning'
    }
    return colors[roleValue] || 'default'
  }

  // 針對特定角色過濾角色選項
  const getRoleOptionsForUser = userLevel => {
    if (userLevel === 'admin') return roleOptions
    if (userLevel === 'non-admin') return roleOptions.filter(option => option.value !== 'admin')
    return roleOptions
  }

  // 時段相關函數
  const getTimeSlotIcon = timeSlot => {
    return timeSlotConfig[timeSlot]?.icon || '🌅'
  }

  const getTimeSlotDisplay = timeSlot => {
    return timeSlotConfig[timeSlot]?.label || '早上'
  }

  const getTimeSlotWithIcon = timeSlot => {
    const config = timeSlotConfig[timeSlot]
    if (!config) return '🌅 早上'
    return `${config.icon} ${config.label}`
  }

  const getNextTimeSlot = currentTimeSlot => {
    return timeSlotConfig[currentTimeSlot]?.next || 'morning'
  }

  // 其他顯示函數
  const getGenderDisplay = genderValue => getOptionLabel(genderOptions, genderValue)
  const getPositionDisplay = positionValue => getOptionLabel(positionOptions, positionValue)
  const getMatchTypeDisplay = value => getOptionLabel(matchTypeOptions, value)
  const getMatchFormatDisplay = value => getOptionLabel(matchFormatOptions, value)

  // ========== 計算屬性 ==========
  const hasOrganizations = computed(() => organizationOptions.value.length > 0)
  const hasPlayers = computed(() => playerOptions.value.length > 0)

  const isGuest = roleValue => {
    return roleValue === 'guest'
  }

  const isManagementRole = roleValue => {
    return ['admin', 'coach', 'cadre'].includes(roleValue)
  }

  return {
    // 靜態選項
    roleOptions,
    genderOptions,
    positionOptions,
    experienceLevelOptions,
    matchTypeOptions,
    matchFormatOptions,
    winLossOptions,
    courtSurfaceOptions,
    courtEnvironmentOptions,
    timeSlotOptions,
    timeSlotOptionsWithIcon,

    // 動態選項
    organizationOptions,
    organizationLoading,
    playerOptions,
    playerLoading,

    // 載入函數
    loadOrganizationOptions,
    loadPlayerOptions,

    // 輔助函數
    getOptionLabel,
    isValidOption,
    getRoleOptionsForUser,

    // 顯示函數
    getExperienceIcon,
    getExperienceLevelDisplay,
    getExperienceWithIcon,
    getTimeSlotIcon,
    getTimeSlotDisplay,
    getTimeSlotWithIcon,
    getNextTimeSlot,
    getRoleDisplay,
    getRoleColor,
    getGenderDisplay,
    getPositionDisplay,
    getMatchTypeDisplay,
    getMatchFormatDisplay,

    // 計算屬性
    hasOrganizations,
    hasPlayers,
    isGuest,
    isManagementRole
  }
}
