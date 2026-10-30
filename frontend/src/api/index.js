/**
 * 每個資源一個模組，元件只透過這裡呼叫後端。
 * 單筆資料直接回傳 data；列表回傳 { items, meta }（meta 為分頁等資訊）。
 */
export { default as authApi } from './auth'
export { default as boardsApi } from './boards'
export { default as eventsApi } from './events'
export { default as guestsApi } from './guests'
export { default as leaderboardApi } from './leaderboard'
export { default as matchesApi } from './matches'
export { default as membersApi } from './members'
export { default as organizationsApi } from './organizations'
export { default as profileApi } from './profile'
export { default as seasonsApi } from './seasons'
