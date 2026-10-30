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
