/** 賽季的日期範圍，例如「2024-08-01 – 2026-10-29」；進行中的賽季為「2026-10-30 起」。 */
export function seasonRangeLabel(season) {
  if (!season) return ''
  return season.end_date ? `${season.start_date} – ${season.end_date}` : `${season.start_date} 起`
}

/** 下拉選單用的選項。 */
export function seasonOptions(seasons) {
  return seasons.map(season => ({ label: season.name, value: season.id }))
}

/** 學年從 8 月開始：2026-10 與 2027-03 都屬於 2026 年開始的學年。 */
function schoolYear(date) {
  return date.getMonth() >= 7 ? date.getFullYear() : date.getFullYear() - 1
}

/** 依民國學年度取預設名稱，例如 2026-10 為「115 學年度」。 */
export function defaultSeasonName(date = new Date()) {
  return `${schoolYear(date) - 1911} 學年度`
}

/** 這個學年度的開始日期（8 月 1 日），格式 YYYY-MM-DD。 */
export function defaultSeasonStart(date = new Date()) {
  return `${schoolYear(date)}-08-01`
}

/** 名單整理時每位隊員的去向：畢業會轉到校友會；離隊的人還能一起打球，只是不算校隊。 */
export const ROSTER_CHOICES = [
  { value: 'team', label: '校隊' },
  { value: 'alumni', label: '畢業' },
  { value: 'left', label: '離隊' }
]

/** 只送出有變動的隊員；row.status 是目前的隊籍，row.choice 是新賽季的去向。 */
export function rosterPayload(rows) {
  return rows.filter(row => row.choice !== row.status).map(row => ({ member_id: row.member.id, status: row.choice }))
}

/** 各去向的人數，以及有變動的隊員名單（給確認步驟顯示）。 */
export function rosterSummary(rows) {
  return Object.fromEntries(
    ROSTER_CHOICES.map(({ value }) => {
      const picked = rows.filter(row => row.choice === value)
      return [
        value,
        { count: picked.length, moved: picked.filter(row => row.status !== value).map(row => row.member.name) }
      ]
    })
  )
}
