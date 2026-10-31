import { dateToTimestamp, formatDate } from './format'
import { MAX_POSSIBLE_GAMES } from './matchRules'

/** 表單用每局比分欄位 game{n}_a_score / game{n}_b_score 的名稱。 */
export const gameField = (gameNumber, side) => `game${gameNumber}_${side}_score`

export function emptyGameFields() {
  const fields = {}
  for (let n = 1; n <= MAX_POSSIBLE_GAMES; n++) {
    fields[gameField(n, 'a')] = 0
    fields[gameField(n, 'b')] = 0
  }
  return fields
}

export function gameScoresFromForm(form) {
  return Array.from({ length: MAX_POSSIBLE_GAMES }, (_, i) => ({
    a: form[gameField(i + 1, 'a')] || 0,
    b: form[gameField(i + 1, 'b')] || 0
  }))
}

export function hasGameScores(form) {
  return gameScoresFromForm(form).some(({ a, b }) => a > 0 || b > 0)
}

export function newMatchForm() {
  return {
    match_date_ts: Date.now(),
    match_type: 'doubles',
    match_format: 'games_9',
    category: 'internal',
    event_id: null,
    session_id: null,
    a_front_id: null,
    b_front_id: null,
    player1_id: null,
    player2_id: null,
    player3_id: null,
    player4_id: null,
    a_games: 0,
    b_games: 0,
    match_notes: '',
    court_surface: 'hard_court',
    court_environment: 'outdoor',
    time_slot: 'evening',
    duration_minutes: null,
    youtube_url: '',
    first_serve_side: null,
    ...emptyGameFields()
  }
}

/** 後端比賽紀錄 → 表單資料。 */
export function matchFormFromRecord(record) {
  const form = newMatchForm()
  for (const game of record.games || []) {
    form[gameField(game.game, 'a')] = game.a_score
    form[gameField(game.game, 'b')] = game.b_score
  }
  return {
    ...form,
    match_date_ts: dateToTimestamp(record.match_date) ?? Date.now(),
    match_type: record.match_type || 'doubles',
    match_format: record.match_format || 'games_9',
    category: record.category || 'internal',
    event_id: record.event?.id ?? null,
    session_id: record.session_id ?? null,
    a_front_id: record.a_front_id ?? null,
    b_front_id: record.b_front_id ?? null,
    player1_id: record.player1_id ?? null,
    player2_id: record.player2_id ?? null,
    player3_id: record.player3_id ?? null,
    player4_id: record.player4_id ?? null,
    a_games: record.a_games || 0,
    b_games: record.b_games || 0,
    match_notes: record.notes || '',
    court_surface: record.court_surface || null,
    court_environment: record.court_environment || null,
    time_slot: record.time_slot || null,
    duration_minutes: record.duration_minutes || null,
    youtube_url: record.youtube_url || '',
    first_serve_side: record.first_serve_side || null
  }
}

/** 表單資料 → 送給後端的 payload。 */
export function matchPayloadFromForm(form) {
  const singles = form.match_type === 'singles'
  const payload = {
    match_date: formatDate(form.match_date_ts),
    match_type: form.match_type,
    match_format: form.match_format,
    category: form.category || 'internal',
    // 只有賽事分類才帶賽事
    event_id: form.category === 'event' ? form.event_id : null,
    player1_id: form.player1_id,
    // 搭檔欄位一律送出（單打時為 null），改成單打時才能清掉原本的搭檔
    player2_id: singles ? null : form.player2_id,
    player3_id: form.player3_id,
    player4_id: singles ? null : form.player4_id,
    // 前衛只有雙打才有；不在該隊（例如換了人）就不送
    a_front_id: !singles && [form.player1_id, form.player2_id].includes(form.a_front_id) ? form.a_front_id : null,
    b_front_id: !singles && [form.player3_id, form.player4_id].includes(form.b_front_id) ? form.b_front_id : null,
    session_id: form.session_id || null,
    a_games: form.a_games,
    b_games: form.b_games,
    notes: form.match_notes || null,
    court_surface: form.court_surface || null,
    court_environment: form.court_environment || null,
    time_slot: form.time_slot || null,
    duration_minutes: form.duration_minutes || null,
    youtube_url: form.youtube_url || null
  }
  if (hasGameScores(form)) {
    payload.first_serve_side = form.first_serve_side || null
    payload.games = gameScoresFromForm(form).map(({ a, b }) => ({ a_score: a, b_score: b }))
  }

  const keepNull = new Set(['player2_id', 'player4_id'])
  return Object.fromEntries(
    Object.entries(payload).filter(([key, value]) => keepNull.has(key) || (value !== null && value !== ''))
  )
}

const PLAYER_FIELDS = ['player1_id', 'player2_id', 'player3_id', 'player4_id']

/** 一頁式記錄送出前的檢查，回傳錯誤訊息或空字串。 */
export function recordFormError(form) {
  if (!form.match_date_ts) return '請選擇比賽日期'
  if (form.category === 'event' && !form.event_id) return '請選擇賽事'
  const fields = form.match_type === 'singles' ? ['player1_id', 'player3_id'] : PLAYER_FIELDS
  const chosen = fields.map(field => form[field])
  if (!chosen.every(Boolean)) return '請選齊兩隊的球員'
  if (new Set(chosen).size !== chosen.length) return '同一位球員不能出現兩次'
  if (!form.a_games && !form.b_games) return '請輸入比分'
  return form.a_games === form.b_games ? '比賽不能平手' : ''
}
