import { describe, expect, it } from 'vitest'
import { gameField, matchFormFromRecord, matchPayloadFromForm, newMatchForm } from '../matchForm'

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
