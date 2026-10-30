import { describe, expect, it } from 'vitest'
import { AVATAR_TONES, identicon } from '../identicon'

describe('identicon', () => {
  it('is the same every time for the same seed', () => {
    expect(identicon(12)).toEqual(identicon(12))
    expect(identicon('山嵜一花')).toEqual(identicon('山嵜一花'))
  })

  it('differs between people', () => {
    expect(identicon(1)).not.toEqual(identicon(2))
  })

  it('picks one of the theme tones', () => {
    const tones = new Set(Array.from({ length: 40 }, (_, id) => identicon(id).tone))
    expect([...tones].every(tone => Number.isInteger(tone) && tone >= 0 && tone < AVATAR_TONES)).toBe(true)
    expect(tones.size).toBeGreaterThan(4)
  })

  it('is mirrored left to right inside a 5x5 grid', () => {
    for (const seed of [1, 7, 42, 'guest']) {
      const { cells } = identicon(seed)
      const keys = new Set(cells.map(([x, y]) => `${x},${y}`))
      expect(cells.length).toBeGreaterThanOrEqual(3)
      for (const [x, y] of cells) {
        expect(x).toBeGreaterThanOrEqual(0)
        expect(y).toBeLessThan(5)
        expect(keys.has(`${4 - x},${y}`)).toBe(true)
      }
    }
  })
})
