import { describe, expect, it } from 'vitest'
import {
  defaultSeasonName,
  defaultSeasonStart,
  rosterPayload,
  rosterSummary,
  seasonOptions,
  seasonRangeLabel
} from '../season'

describe('seasonRangeLabel', () => {
  it('shows both ends for a finished season', () => {
    expect(seasonRangeLabel({ start_date: '2024-08-01', end_date: '2026-10-29' })).toBe('2024-08-01 – 2026-10-29')
  })

  it('shows only the start for the current season', () => {
    expect(seasonRangeLabel({ start_date: '2026-10-30', end_date: null })).toBe('2026-10-30 起')
    expect(seasonRangeLabel(null)).toBe('')
  })
})

describe('seasonOptions', () => {
  it('lists seasons by name', () => {
    const options = seasonOptions([
      { id: 2, name: '115 學年度', is_current: true },
      { id: 1, name: '113 學年度', is_current: false }
    ])
    expect(options).toEqual([
      { label: '115 學年度', value: 2 },
      { label: '113 學年度', value: 1 }
    ])
  })
})

describe('defaultSeasonName', () => {
  it('follows the school year starting in August', () => {
    expect(defaultSeasonName(new Date(2026, 9, 30))).toBe('115 學年度')
    expect(defaultSeasonName(new Date(2027, 2, 1))).toBe('115 學年度')
    expect(defaultSeasonName(new Date(2027, 7, 1))).toBe('116 學年度')
  })

  it('starts the school year on August 1st', () => {
    expect(defaultSeasonStart(new Date(2026, 9, 30))).toBe('2026-08-01')
    expect(defaultSeasonStart(new Date(2027, 2, 1))).toBe('2026-08-01')
  })
})

describe('roster helpers', () => {
  const rows = [
    { member: { id: 1, name: '甲' }, status: 'team', choice: 'team' },
    { member: { id: 2, name: '乙' }, status: 'team', choice: 'alumni' },
    { member: { id: 3, name: '丙' }, status: 'alumni', choice: 'left' },
    { member: { id: 4, name: '丁' }, status: 'alumni', choice: 'alumni' }
  ]

  it('sends only the changed members', () => {
    expect(rosterPayload(rows)).toEqual([
      { member_id: 2, status: 'alumni' },
      { member_id: 3, status: 'left' }
    ])
  })

  it('counts each choice and lists who moved', () => {
    expect(rosterSummary(rows)).toEqual({
      team: { count: 1, moved: [] },
      alumni: { count: 2, moved: ['乙'] },
      left: { count: 1, moved: ['丙'] }
    })
  })
})
