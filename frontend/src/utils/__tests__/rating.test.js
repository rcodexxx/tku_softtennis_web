import { describe, expect, it } from 'vitest'
import { formatRating, isRated, ratingPercent } from '../rating'

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
