import { describe, expect, it } from 'vitest'
import { formatRating, rankPlayers, ratingPercent } from '../rating'

describe('rating', () => {
  it('formatRating 顯示到小數點一位', () => {
    expect(formatRating(5.44)).toBe('5.4')
    expect(formatRating(5)).toBe('5.0')
    expect(formatRating(null)).toBe('—')
  })

  it('ratingPercent 換算 1–10 的位置', () => {
    expect(ratingPercent(1)).toBe(0)
    expect(ratingPercent(5.5)).toBe(50)
    expect(ratingPercent(12)).toBe(100)
    expect(ratingPercent(undefined)).toBe(0)
  })
})

describe('rankPlayers', () => {
  const players = [
    { id: 1, name: '甲', rating: 5.2, total_matches: 6 },
    { id: 2, name: '乙', rating: 5.0, total_matches: 0 },
    { id: 3, name: '丙', rating: 6.1, total_matches: 8 },
    { id: 4, name: '丁', rating: 4.4, total_matches: 1 }
  ]

  it('ranks everyone who has played, by score', () => {
    const { ranked, unranked } = rankPlayers(players)
    expect(ranked.map(p => [p.id, p.rank])).toEqual([
      [3, 1],
      [1, 2],
      [4, 3]
    ])
    expect(unranked.map(p => [p.id, p.rank])).toEqual([[2, null]])
  })

  it('uses the given sort key', () => {
    const { ranked } = rankPlayers(players, p => p.total_matches)
    expect(ranked.map(p => p.id)).toEqual([3, 1, 4])
  })
})
