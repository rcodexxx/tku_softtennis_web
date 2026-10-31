import { describe, expect, it } from 'vitest'
import { gameField, matchFormFromRecord, matchPayloadFromForm, newMatchForm, recordFormError } from '../matchForm'

const record = {
  id: 65,
  match_date: '2025-06-29',
  match_type: 'doubles',
  match_format: 'games_7',
  player1_id: 1,
  player2_id: 2,
  player3_id: 3,
  player4_id: 4,
  a_games: 4,
  b_games: 1,
  notes: '冠軍賽',
  court_surface: 'hard_court',
  court_environment: null,
  time_slot: 'evening',
  first_serve_side: 'side_b',
  games: [
    { game: 1, a_score: 4, b_score: 2 },
    { game: 2, a_score: 1, b_score: 4 }
  ]
}

describe('比賽紀錄 ↔ 表單', () => {
  it('把 games 陣列展開成每局欄位', () => {
    const form = matchFormFromRecord(record)
    expect(form[gameField(1, 'a')]).toBe(4)
    expect(form[gameField(2, 'b')]).toBe(4)
    expect(form[gameField(3, 'a')]).toBe(0)
    expect(form.match_notes).toBe('冠軍賽')
  })

  it('只有賽事分類會帶賽事', () => {
    const base = { ...newMatchForm(), player1_id: 1, player3_id: 3, a_games: 4 }
    expect(matchPayloadFromForm({ ...base, category: 'event', event_id: 7 })).toMatchObject({
      category: 'event',
      event_id: 7
    })
    const friendly = matchPayloadFromForm({ ...base, category: 'friendly', event_id: 7 })
    expect(friendly.category).toBe('friendly')
    expect(friendly).not.toHaveProperty('event_id')
  })

  it('表單轉回 payload 時日期和比分不變', () => {
    const payload = matchPayloadFromForm(matchFormFromRecord(record))
    expect(payload.match_date).toBe('2025-06-29')
    expect(payload.notes).toBe('冠軍賽')
    expect(payload.first_serve_side).toBe('side_b')
    expect(payload.games).toHaveLength(9)
    expect(payload.games.slice(0, 2)).toEqual([
      { a_score: 4, b_score: 2 },
      { a_score: 1, b_score: 4 }
    ])
    expect(payload).not.toHaveProperty('court_environment')
  })

  it('沒有每局比分時不送 games', () => {
    const payload = matchPayloadFromForm({ ...newMatchForm(), player1_id: 1, player3_id: 3, a_games: 4 })
    expect(payload).not.toHaveProperty('games')
  })

  it('單打會清掉搭檔，混雙不會', () => {
    const doubles = { ...matchFormFromRecord(record) }
    expect(matchPayloadFromForm({ ...doubles, match_type: 'singles' })).toMatchObject({
      player2_id: null,
      player4_id: null
    })
    expect(matchPayloadFromForm({ ...doubles, match_type: 'mixed_doubles' })).toMatchObject({
      player2_id: 2,
      player4_id: 4
    })
  })
})

describe('recordFormError', () => {
  const ready = {
    ...newMatchForm(),
    player1_id: 1,
    player2_id: 2,
    player3_id: 3,
    player4_id: 4,
    a_games: 4,
    b_games: 2
  }

  it('accepts a complete doubles match', () => {
    expect(recordFormError(ready)).toBe('')
    expect(recordFormError({ ...ready, match_type: 'singles', player2_id: null, player4_id: null })).toBe('')
  })

  it('explains what is missing', () => {
    expect(recordFormError({ ...ready, player4_id: null })).toBe('請選齊兩隊的球員')
    expect(recordFormError({ ...ready, player4_id: 1 })).toBe('同一位球員不能出現兩次')
    expect(recordFormError({ ...ready, a_games: 0, b_games: 0 })).toBe('請輸入比分')
    expect(recordFormError({ ...ready, b_games: 4 })).toBe('比賽不能平手')
    expect(recordFormError({ ...ready, category: 'event', event_id: null })).toBe('請選擇賽事')
  })
})
