import { describe, expect, it } from 'vitest'
import { formatChemistry, usualFormation } from '../pairs'

describe('formatChemistry', () => {
  it('shows a sign for real differences', () => {
    expect(formatChemistry(0.43)).toBe('+0.4')
    expect(formatChemistry(-0.26)).toBe('-0.3')
    expect(formatChemistry(0.02)).toBe('0.0')
    expect(formatChemistry(null)).toBe('—')
  })
})

describe('usualFormation', () => {
  const pair = {
    players: [
      { id: 1, name: '甲' },
      { id: 2, name: '乙' }
    ],
    fronts: { 2: 5, 1: 1 }
  }

  it('picks who usually plays at the net', () => {
    expect(usualFormation(pair)).toEqual({ front: { id: 2, name: '乙' }, back: { id: 1, name: '甲' } })
    expect(usualFormation({ ...pair, fronts: {} })).toBeNull()
  })
})
