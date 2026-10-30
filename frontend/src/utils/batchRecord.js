import { gameScoresFromForm, hasGameScores, matchPayloadFromForm, newMatchForm } from './matchForm'
import { countGamesWon, gamesToWin } from './matchRules'

/** 批次記錄的一列：比賽表單 + 列的識別碼與伺服器錯誤。 */
let nextKey = 1
export function newBatchRow(defaults = {}) {
  return { ...newMatchForm(), key: `row-${Date.now()}-${nextKey++}`, server_error: '', ...defaults }
}

/** 新的一列沿用上一列的日期、類型與賽制（通常是同一天的連續比賽）。 */
export function rowDefaultsFrom(row) {
  if (!row) return {}
  return { match_date_ts: row.match_date_ts, match_type: row.match_type, match_format: row.match_format }
}

/** 解析總局數：接受 4-2、4:2、4 2、42 等寫法。 */
export function parseScoreText(text) {
  const value = String(text ?? '').trim()
  if (!value) return null
  const match = value.match(/^(\d+)\s*[-:：/\s]\s*(\d+)$/) || value.match(/^(\d)(\d)$/)
  if (!match) return null
  return { a: Number(match[1]), b: Number(match[2]) }
}

export function scoreText(row) {
  if (!row.a_games && !row.b_games) return ''
  return `${row.a_games}-${row.b_games}`
}

const playerIds = row =>
  row.match_type === 'singles'
    ? [row.player1_id, row.player3_id]
    : [row.player1_id, row.player2_id, row.player3_id, row.player4_id]

export function isEmptyRow(row) {
  return !playerIds(row).some(Boolean) && !row.a_games && !row.b_games && !hasGameScores(row)
}

/**
 * 一列的狀態：
 * - empty：完全沒填，儲存時略過
 * - incomplete：還沒填完（message 說明缺什麼）
 * - invalid：填了但不合理（例如球員重複、比分不可能）
 * - ready：可以儲存
 */
export function rowStatus(row) {
  if (isEmptyRow(row)) return { state: 'empty', message: '' }
  if (row.server_error) return { state: 'invalid', message: row.server_error }

  const ids = playerIds(row)
  const chosen = ids.filter(Boolean)
  if (new Set(chosen).size !== chosen.length) return { state: 'invalid', message: '同一位球員重複出現' }

  if (hasGameScores(row)) {
    const { error } = countGamesWon(gameScoresFromForm(row), row.match_format)
    if (error) return { state: 'invalid', message: `第 ${error.game} 局：${error.message}` }
  }
  const toWin = gamesToWin(row.match_format)
  const high = Math.max(row.a_games, row.b_games)
  const low = Math.min(row.a_games, row.b_games)
  if (high > toWin || (high === toWin && low >= toWin)) {
    return { state: 'invalid', message: `比分不合理：先贏 ${toWin} 局就結束` }
  }

  const missing = []
  if (chosen.length < ids.length) missing.push(`${ids.length - chosen.length} 位球員`)
  if (high < toWin) missing.push('比分')
  if (missing.length) return { state: 'incomplete', message: `還缺 ${missing.join('、')}` }
  return { state: 'ready', message: '' }
}

export function winnerOf(row) {
  const toWin = gamesToWin(row.match_format)
  if (row.a_games === toWin && row.b_games < toWin) return 'a'
  if (row.b_games === toWin && row.a_games < toWin) return 'b'
  return null
}

/** 把可儲存的列轉成 API payload；shared 為整批共用的場地與時段。 */
export function batchPayload(rows, shared = {}) {
  return rows.map(row => matchPayloadFromForm({ ...row, ...shared }))
}

/** 把後端 details（{ records: { "1": {...} } }）轉成「第幾筆 → 錯誤訊息」。 */
export function batchErrorsByIndex(details) {
  const records = details?.records
  if (!records || typeof records !== 'object' || Array.isArray(records)) return {}
  const flatten = value =>
    Array.isArray(value)
      ? value.flatMap(flatten)
      : value && typeof value === 'object'
        ? Object.values(value).flatMap(flatten)
        : [String(value)]
  return Object.fromEntries(Object.entries(records).map(([index, value]) => [Number(index), flatten(value).join('；')]))
}
