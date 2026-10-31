/** 校內球員的身分，對應後端 MemberIdentityEnum。 */
export const IDENTITY_OPTIONS = [
  { value: 'student', label: '在校生' },
  { value: 'exchange', label: '交換生' },
  { value: 'coach', label: '教練' },
  { value: 'alumni', label: '校友' },
  { value: 'other', label: '其他' }
]

const pick = values => IDENTITY_OPTIONS.filter(option => values.includes(option.value))
/** 校隊與校友會各自可選的身分（校友會的人不是校內成員）。 */
export const IDENTITIES_BY_KIND = {
  team: pick(['student', 'exchange', 'coach', 'other']),
  alumni: pick(['alumni', 'coach'])
}

export const PROGRAM_OPTIONS = [
  { value: 'bachelor', label: '大學部' },
  { value: 'master', label: '碩士' },
  { value: 'phd', label: '博士' }
]

/**
 * 從學號推測學制與入學學年度（只是預填，可以改）：
 * 第一碼 4 視為大學部、6 視為碩士，接著兩碼是入學學年度的後兩位，例如 413… → 大學部 113 學年度入學。
 */
export function guessFromStudentId(studentId) {
  const match = /^([46])(\d{2})\d{6}$/.exec(String(studentId ?? '').trim())
  if (!match) return null
  return { study_program: match[1] === '4' ? 'bachelor' : 'master', enrolled_year: 100 + Number(match[2]) }
}
