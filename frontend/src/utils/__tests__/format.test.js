import { describe, expect, it } from 'vitest'
import { dateToTimestamp, formatDate, formatDisplayScore, formatScore } from '../format'

describe('日期', () => {
  it('以本地時區輸出 YYYY-MM-DD', () => {
    expect(formatDate(new Date(2025, 5, 9, 23, 59))).toBe('2025-06-09')
    expect(formatDate(new Date(2025, 0, 1, 0, 0).getTime())).toBe('2025-01-01')
  })

  it('空值與無效日期回傳 null', () => {
    expect(formatDate(null)).toBeNull()
    expect(formatDate('')).toBeNull()
    expect(formatDate('not a date')).toBeNull()
  })

  it('YYYY-MM-DD 轉時間戳再轉回來不變', () => {
    expect(formatDate(dateToTimestamp('2025-06-29'))).toBe('2025-06-29')
    expect(dateToTimestamp(null)).toBeNull()
  })
})

describe('分數', () => {
  it('固定小數位數', () => {
    expect(formatScore(12.345, 2)).toBe('12.35')
    expect(formatScore(undefined)).toBe('0.0')
  })

  it('排行榜分數乘以 100 取整數', () => {
    expect(formatDisplayScore(25.704)).toBe('2570')
    expect(formatDisplayScore(null)).toBe('0')
  })
})
