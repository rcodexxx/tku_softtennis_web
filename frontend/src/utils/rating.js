/**
 * 與後端 domain/rating.py 對應：分數 1–10，顯示到小數點一位。
 * 分數由最近 20 場的局數表現算出；少於 RATED_MATCHES 場時還在評估中。
 */
export const MIN_RATING = 1
export const MAX_RATING = 10
export const RATED_MATCHES = 5

export function formatRating(value) {
  return typeof value === 'number' && !Number.isNaN(value) ? value.toFixed(1) : '—'
}

/** 分數在 1–10 之間的位置（0–100），給進度條用。 */
export function ratingPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 0
  return Math.max(0, Math.min(100, ((value - MIN_RATING) / (MAX_RATING - MIN_RATING)) * 100))
}

export function isRated(totalMatches) {
  return (totalMatches ?? 0) >= RATED_MATCHES
}

/**
 * 排行榜名單：打滿 RATED_MATCHES 場的人依 sortKey 排名（rank 從 1 開始）；
 * 其他人排在後面、沒有名次，打過比較多場的在前。
 */
export function rankPlayers(players, sortKey = player => player.rating) {
  const ranked = players
    .filter(player => isRated(player.total_matches))
    .sort((a, b) => sortKey(b) - sortKey(a))
    .map((player, index) => ({ ...player, rank: index + 1 }))
  const unranked = players
    .filter(player => !isRated(player.total_matches))
    .sort((a, b) => b.total_matches - a.total_matches || b.rating - a.rating)
    .map(player => ({ ...player, rank: null }))
  return { ranked, unranked }
}
