import { describe, expect, it } from 'vitest'
import { headToHeadHighlights } from '../insights'

const entry = (id, wins, losses) => ({
  player: { id },
  wins,
  losses,
  matches: wins + losses,
  win_rate: Math.round((wins / (wins + losses)) * 1000) / 10
})

describe('headToHeadHighlights', () => {
  it('picks the best partner, nemesis and favourite opponent', () => {
    const partners = [entry(1, 3, 1), entry(2, 1, 0), entry(3, 2, 2)]
    const opponents = [entry(4, 0, 3), entry(5, 4, 1), entry(6, 1, 1)]
    const { bestPartner, nemesis, favorite } = headToHeadHighlights(partners, opponents)
    expect(bestPartner.player.id).toBe(1)
    expect(nemesis.player.id).toBe(4)
    expect(favorite.player.id).toBe(5)
  })

  it('needs enough matches and a real edge', () => {
    const result = headToHeadHighlights([entry(1, 1, 0)], [entry(2, 1, 1)])
    expect(result).toEqual({ bestPartner: null, nemesis: null, favorite: null })
  })
})
