/** 比賽分類，對應後端 MatchCategoryEnum。 */
export const MATCH_CATEGORIES = [
  { value: 'internal', label: '隊內' },
  { value: 'friendly', label: '友誼賽' },
  { value: 'event', label: '賽事' }
]

/** 比賽卡片上的標籤：隊內不標，友誼賽標「友誼賽」，賽事標賽事名稱。 */
export function categoryTag(record) {
  if (record.category === 'event') return record.event?.name ?? '賽事'
  if (record.category === 'friendly') return '友誼賽'
  return null
}

/** 賽事日期：單日「2025-03-01」，多日「2025-03-01 – 03-03」。 */
export function eventDateLabel(event) {
  if (!event?.start_date) return ''
  if (!event.end_date || event.end_date === event.start_date) return event.start_date
  const sameYear = event.end_date.slice(0, 4) === event.start_date.slice(0, 4)
  return `${event.start_date} – ${sameYear ? event.end_date.slice(5) : event.end_date}`
}
