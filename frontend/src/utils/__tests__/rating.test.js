import { describe, expect, it } from 'vitest'
import { formatRating, isRated, rankPlayers, ratingPercent } from '../rating'

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

  it('打滿 5 場才有正式分數', () => {
    expect(isRated(4)).toBe(false)
    expect(isRated(5)).toBe(true)
    expect(isRated(undefined)).toBe(false)
  })
})

describe('rankPlayers', () => {
  const players = [
    { id: 1, rating: 5.2, total_matches: 6 },
    { id: 2, rating: 5.0, total_matches: 0 },
    { id: 3, rating: 6.1, total_matches: 8 },
    { id: 4, rating: 4.4, total_matches: 2 }
  ]

  it('ranks only players with enough matches', () => {
    const { ranked, unranked } = rankPlayers(players)
    expect(ranked.map(p => [p.id, p.rank])).toEqual([
      [3, 1],
      [1, 2]
    ])
    expect(unranked.map(p => [p.id, p.rank])).toEqual([
      [4, null],
      [2, null]
    ])
  })

  it('uses the given sort key', () => {
    const { ranked } = rankPlayers(players, p => p.total_matches)
    expect(ranked.map(p => p.id)).toEqual([3, 1])
  })
})
