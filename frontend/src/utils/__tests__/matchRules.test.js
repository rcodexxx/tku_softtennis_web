import { describe, expect, it } from 'vitest'
import {
  countGamesWon,
  gamesToWin,
  isTiebreakGame,
  maxGames,
  quickResults,
  serveSideForGame,
  tiebreakScore,
  validateGameScore
} from '../matchRules'

describe('賽制', () => {
  it.each([
    ['games_5', 5, 3],
    ['games_7', 7, 4],
    ['games_9', 9, 5]
  ])('%s：最多 %i 局，先贏 %i 局', (format, max, toWin) => {
    expect(maxGames(format)).toBe(max)
    expect(gamesToWin(format)).toBe(toWin)
    expect(isTiebreakGame(format, max)).toBe(true)
    expect(isTiebreakGame(format, max - 1)).toBe(false)
  })

  it('未知賽制預設九局、沒有決勝局', () => {
    expect(maxGames(undefined)).toBe(9)
    expect(isTiebreakGame(undefined, 9)).toBe(false)
  })
})

describe('發球輪替', () => {
  it('奇數局由先發方發球', () => {
    expect([1, 2, 3].map(n => serveSideForGame('side_a', n))).toEqual(['side_a', 'side_b', 'side_a'])
    expect(serveSideForGame('side_b', 2)).toBe('side_a')
    expect(serveSideForGame(null, 1)).toBeNull()
  })
})

describe('單局比分', () => {
  it.each([
    [4, 0, false, true, 'A'],
    [4, 2, false, true, 'A'],
    [3, 3, false, false, null],
    [4, 3, false, false, null],
    [5, 3, false, true, 'A'],
    [6, 8, false, true, 'B'],
    [7, 5, true, true, 'A'],
    [6, 6, true, false, null],
    [7, 6, true, false, null],
    [6, 8, true, true, 'B'],
    [0, 0, false, false, null]
  ])('%i:%i（決勝局 %s）→ 結束 %s，勝方 %s', (a, b, tiebreak, finished, winner) => {
    const result = validateGameScore(a, b, tiebreak)
    expect(result.isValid).toBe(true)
    expect(result.gameFinished).toBe(finished)
    expect(result.winner).toBe(winner)
  })

  it('負分與過高分數無效', () => {
    expect(validateGameScore(-1, 0).isValid).toBe(false)
    expect(validateGameScore(51, 49).isValid).toBe(false)
  })
})

describe('計算勝局數', () => {
  it('依每局比分累計，忽略未進行的局', () => {
    const scores = [
      { a: 4, b: 1 },
      { a: 2, b: 4 },
      { a: 4, b: 0 },
      { a: 0, b: 0 },
      { a: 7, b: 5 }
    ]
    expect(countGamesWon(scores, 'games_5')).toEqual({ aWins: 3, bWins: 1, error: null })
  })

  it('遇到無效比分時回報局數', () => {
    expect(
      countGamesWon(
        [
          { a: 4, b: 1 },
          { a: -1, b: 0 }
        ],
        'games_5'
      ).error
    ).toEqual({
      game: 2,
      message: '分數不能為負數'
    })
  })
})

describe('列表的決勝局比分', () => {
  const games = [{ game: 7, a_score: 5, b_score: 7 }]

  it('打到決勝局時回傳最後一局比分', () => {
    expect(tiebreakScore({ match_format: 'games_7', a_games: 3, b_games: 4, games })).toEqual({
      aScore: 5,
      bScore: 7,
      gameNumber: 7
    })
  })

  it('沒有打到決勝局或沒有每局比分時回傳 null', () => {
    expect(tiebreakScore({ match_format: 'games_7', a_games: 4, b_games: 1, games })).toBeNull()
    expect(tiebreakScore({ match_format: 'games_7', a_games: 3, b_games: 4, games: [] })).toBeNull()
  })
})

describe('quickResults', () => {
  it('lists every winning score for the format', () => {
    const { a, b } = quickResults('games_7')
    expect(a).toEqual([
      { a: 4, b: 0 },
      { a: 4, b: 1 },
      { a: 4, b: 2 },
      { a: 4, b: 3 }
    ])
    expect(b.at(-1)).toEqual({ a: 3, b: 4 })
    expect(quickResults('games_5').a).toHaveLength(3)
  })
})
