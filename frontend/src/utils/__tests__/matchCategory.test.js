import { describe, expect, it } from 'vitest'
import { categoryTag, eventDateLabel } from '../matchCategory'

describe('categoryTag', () => {
  it('labels friendly and event matches only', () => {
    expect(categoryTag({ category: 'internal' })).toBeNull()
    expect(categoryTag({ category: 'friendly' })).toBe('友誼賽')
    expect(categoryTag({ category: 'event', event: { id: 1, name: '淡江盃' } })).toBe('淡江盃')
    expect(categoryTag({ category: 'event', event: null })).toBe('賽事')
  })
})

describe('eventDateLabel', () => {
  it('shows one day or a range', () => {
    expect(eventDateLabel({ start_date: '2025-03-01', end_date: null })).toBe('2025-03-01')
    expect(eventDateLabel({ start_date: '2025-03-01', end_date: '2025-03-03' })).toBe('2025-03-01 – 03-03')
    expect(eventDateLabel({ start_date: '2025-12-30', end_date: '2026-01-02' })).toBe('2025-12-30 – 2026-01-02')
    expect(eventDateLabel({})).toBe('')
  })
})
