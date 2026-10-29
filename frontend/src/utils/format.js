/** 轉成本地時區的 YYYY-MM-DD；可接受時間戳、Date 或日期字串。 */
export function formatDate(value) {
  if (value === null || value === undefined || value === '') return null
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return null
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

/** 把 YYYY-MM-DD 轉成本地午夜的時間戳（給 n-date-picker 用）。 */
export function dateToTimestamp(dateString) {
  if (!dateString) return null
  const [year, month, day] = dateString.split('-').map(Number)
  return new Date(year, month - 1, day).getTime()
}

/** 固定小數位數；非數字時回傳 0 的對應格式。 */
export function formatScore(score, precision = 1) {
  const value = typeof score === 'number' && !Number.isNaN(score) ? score : 0
  return value.toFixed(precision)
}

/** 排行榜顯示用的分數：conservative_score × 100 取整數。 */
export function formatDisplayScore(score) {
  if (typeof score !== 'number' || Number.isNaN(score)) return '0'
  return Math.round(score * 100).toString()
}
