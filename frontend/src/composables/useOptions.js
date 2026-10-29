import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import { organizationsApi } from '@/api'

// 與後端 enums 對應的選項
const roleOptions = [
  { label: '隊員', value: 'member' },
  { label: '幹部', value: 'cadre' },
  { label: '教練', value: 'coach' },
  { label: '管理員', value: 'admin' }
]
const genderOptions = [
  { label: '男性', value: 'male' },
  { label: '女性', value: 'female' }
]
const positionOptions = [
  { label: '後排', value: 'back' },
  { label: '前排', value: 'front' },
  { label: '皆可', value: 'versatile' }
]
const matchTypeOptions = [
  { label: '雙打', value: 'doubles' },
  { label: '單打', value: 'singles' }
]
const matchFormatOptions = [
  { label: '五局制', value: 'games_5' },
  { label: '七局制', value: 'games_7' },
  { label: '九局制', value: 'games_9' }
]
const winLossOptions = [
  { label: '勝利', value: 'win' },
  { label: '失敗', value: 'loss' }
]
const courtSurfaceOptions = [
  { label: '硬地球場', value: 'hard_court' },
  { label: '紅土球場', value: 'clay_court' },
  { label: '草地球場', value: 'grass_court' }
]
const courtEnvironmentOptions = [
  { label: '室外', value: 'outdoor' },
  { label: '室內', value: 'indoor' }
]
const timeSlotOptions = [
  { label: '早上', value: 'morning' },
  { label: '下午', value: 'afternoon' },
  { label: '晚上', value: 'evening' }
]

export function getOptionLabel(options, value) {
  return options.find(option => option.value === value)?.label ?? value
}

/** 下拉選單選項與顯示文字；組織選項需要呼叫 loadOrganizationOptions 載入。 */
export function useOptions() {
  const message = useMessage()
  const organizationOptions = ref([])
  const organizationLoading = ref(false)

  const loadOrganizationOptions = async () => {
    if (organizationOptions.value.length) return
    organizationLoading.value = true
    try {
      const organizations = await organizationsApi.list()
      organizationOptions.value = organizations.map(org => ({ label: org.name, value: org.id }))
    } catch {
      message.error('載入組織列表失敗')
    } finally {
      organizationLoading.value = false
    }
  }

  return {
    roleOptions,
    genderOptions,
    positionOptions,
    matchTypeOptions,
    matchFormatOptions,
    winLossOptions,
    courtSurfaceOptions,
    courtEnvironmentOptions,
    timeSlotOptions,
    organizationOptions,
    organizationLoading,
    loadOrganizationOptions,
    getOptionLabel,
    getRoleDisplay: value => getOptionLabel(roleOptions, value),
    getGenderDisplay: value => getOptionLabel(genderOptions, value),
    getPositionDisplay: value => getOptionLabel(positionOptions, value),
    getMatchTypeDisplay: value => getOptionLabel(matchTypeOptions, value),
    getMatchFormatDisplay: value => getOptionLabel(matchFormatOptions, value)
  }
}
