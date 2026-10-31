/** 默契值的顯示：+0.4 / -0.2；接近 0 時不加正負號。 */
export function formatChemistry(value) {
  if (typeof value !== 'number') return '—'
  const rounded = Math.round(value * 10) / 10
  if (rounded === 0) return '0.0'
  return `${rounded > 0 ? '+' : ''}${rounded.toFixed(1)}`
}

/** 這組最常的站位：回傳 { front, back }（球員物件），沒記錄過站位就回傳 null。 */
export function usualFormation(pair) {
  const counts = Object.entries(pair.fronts ?? {})
  if (!counts.length) return null
  const [frontId] = counts.sort((a, b) => b[1] - a[1])[0]
  const front = pair.players.find(player => String(player.id) === frontId)
  const back = pair.players.find(player => String(player.id) !== frontId)
  return front && back ? { front, back } : null
}
