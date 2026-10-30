import { describe, expect, it } from 'vitest'
import {
  batchErrorsByIndex,
  batchPayload,
  isEmptyRow,
  newBatchRow,
  parseScoreText,
  rowDefaultsFrom,
  rowStatus,
  winnerOf
} from '../batchRecord'
import { gameField } from '../matchForm'

const doubles = (extra = {}) =>
  newBatchRow({ match_format: 'games_7', player1_id: 1, player2_id: 2, player3_id: 3, player4_id: 4, ...extra })

describe('parseScoreText', () => {
  it.each([
    ['4-2', { a: 4, b: 2 }],
    ['4:2', { a: 4, b: 2 }],
    [' 4 2 ', { a: 4, b: 2 }],
    ['42', { a: 4, b: 2 }],
    ['5：3', { a: 5, b: 3 }]
  ])('%s', (text, expected) => {
    expect(parseScoreText(text)).toEqual(expected)
  })

  it('看不懂的格式回傳 null', () => {
    expect(parseScoreText('')).toBeNull()
    expect(parseScoreText('4')).toBeNull()
    expect(parseScoreText('a-b')).toBeNull()
  })
})

describe('rowStatus', () => {
  it('完全沒填的列是 empty', () => {
    expect(isEmptyRow(newBatchRow())).toBe(true)
    expect(rowStatus(newBatchRow()).state).toBe('empty')
  })

  it('球員與比分都填好才是 ready', () => {
    expect(rowStatus(doubles({ a_games: 4, b_games: 2 })).state).toBe('ready')
    expect(rowStatus(doubles({ a_games: 3, b_games: 2 }))).toEqual({ state: 'incomplete', message: '還缺 比分' })
    expect(rowStatus(doubles({ player4_id: null, a_games: 4, b_games: 0 })).message).toBe('還缺 1 位球員')
  })

  it('單打只需要兩位球員', () => {
    const row = newBatchRow({
      match_type: 'singles',
      match_format: 'games_5',
      player1_id: 1,
      player3_id: 2,
      a_games: 1,
      b_games: 3
    })
    expect(rowStatus(row).state).toBe('ready')
  })

  it('球員重複或比分超過賽制是 invalid', () => {
    expect(rowStatus(doubles({ player4_id: 1 })).state).toBe('invalid')
    expect(rowStatus(doubles({ a_games: 5, b_games: 2 })).state).toBe('invalid')
    expect(rowStatus(doubles({ a_games: 4, b_games: 4 })).state).toBe('invalid')
  })

  it('每局比分有錯會指出第幾局', () => {
    const row = doubles({ [gameField(1, 'a')]: 51, [gameField(1, 'b')]: 0 })
    expect(rowStatus(row)).toMatchObject({ state: 'invalid', message: expect.stringContaining('第 1 局') })
  })

  it('伺服器錯誤優先顯示', () => {
    expect(rowStatus(doubles({ a_games: 4, b_games: 2, server_error: '找不到球員' })).message).toBe('找不到球員')
  })
})

describe('其他', () => {
  it('winnerOf', () => {
    expect(winnerOf(doubles({ a_games: 4, b_games: 2 }))).toBe('a')
    expect(winnerOf(doubles({ a_games: 1, b_games: 4 }))).toBe('b')
    expect(winnerOf(doubles({ a_games: 3, b_games: 2 }))).toBeNull()
  })

  it('新的一列沿用上一列的日期、類型與賽制', () => {
    const previous = doubles({ match_date_ts: 0, match_type: 'singles' })
    expect(rowDefaultsFrom(previous)).toEqual({ match_date_ts: 0, match_type: 'singles', match_format: 'games_7' })
    expect(rowDefaultsFrom(undefined)).toEqual({})
  })

  it('batchPayload 套用共用的場地設定', () => {
    const [payload] = batchPayload([doubles({ a_games: 4, b_games: 2 })], {
      court_surface: 'clay_court',
      time_slot: null
    })
    expect(payload).toMatchObject({ player1_id: 1, a_games: 4, b_games: 2, court_surface: 'clay_court' })
    expect(payload).not.toHaveProperty('time_slot')
    expect(payload).not.toHaveProperty('key')
  })

  it('batchErrorsByIndex 攤平後端的巢狀錯誤', () => {
    const details = { records: { 1: { _schema: ['同一位球員不能重複出現在比賽中。'] }, 3: { a_games: ['不一致'] } } }
    expect(batchErrorsByIndex(details)).toEqual({ 1: '同一位球員不能重複出現在比賽中。', 3: '不一致' })
    expect(batchErrorsByIndex({ records: ['錯'] })).toEqual({})
    expect(batchErrorsByIndex(undefined)).toEqual({})
  })
})
