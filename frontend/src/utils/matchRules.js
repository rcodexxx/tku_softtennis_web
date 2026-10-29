/**
 * 軟式網球的賽制與計分規則。
 * - 一般局：先拿 4 分，3:3 之後要領先 2 分
 * - 決勝局（最後一局）：先拿 7 分，6:6 之後要領先 2 分
 * - 發球：第一局由先發方發球，之後每局輪替
 */

const MAX_GAMES = { games_5: 5, games_7: 7, games_9: 9 }
export const MAX_POSSIBLE_GAMES = 9
const MAX_POINTS = 50

export function maxGames(format) {
  return MAX_GAMES[format] || MAX_POSSIBLE_GAMES
}

export function gamesToWin(format) {
  return Math.ceil(maxGames(format) / 2)
}

export function isTiebreakGame(format, gameNumber) {
  return format in MAX_GAMES && gameNumber === MAX_GAMES[format]
}

export function serveSideForGame(firstServeSide, gameNumber) {
  if (!firstServeSide) return null
  if (gameNumber % 2 === 1) return firstServeSide
  return firstServeSide === 'side_a' ? 'side_b' : 'side_a'
}

/** 單局比分的有效性與勝負：{ isValid, message, gameFinished, winner } */
export function validateGameScore(aScore, bScore, isTiebreak = false) {
  if (aScore < 0 || bScore < 0) return { isValid: false, message: '分數不能為負數' }
  if (aScore > MAX_POINTS || bScore > MAX_POINTS) return { isValid: false, message: '分數過高，請檢查輸入' }

  const pending = { isValid: true, message: '', gameFinished: false, winner: null }
  if (aScore === 0 && bScore === 0) return pending

  const target = isTiebreak ? 7 : 4
  const deuceAt = target - 1
  const low = Math.min(aScore, bScore)
  const high = Math.max(aScore, bScore)
  const finished = { isValid: true, message: '', gameFinished: true, winner: aScore > bScore ? 'A' : 'B' }

  if (low < deuceAt) return high >= target ? finished : pending
  return high - low >= 2 ? finished : pending
}

/** 每局比分陣列 [{ a, b }]（第 1 局在 index 0）計算勝局數；遇到無效比分時回傳錯誤。 */
export function countGamesWon(scores, format) {
  let aWins = 0
  let bWins = 0
  for (let i = 0; i < Math.min(scores.length, maxGames(format)); i++) {
    const { a = 0, b = 0 } = scores[i] || {}
    if (a === 0 && b === 0) continue
    const result = validateGameScore(a, b, isTiebreakGame(format, i + 1))
    if (!result.isValid) {
      return { aWins, bWins, error: { game: i + 1, message: result.message } }
    }
    if (result.winner === 'A') aWins++
    if (result.winner === 'B') bWins++
  }
  return { aWins, bWins, error: null }
}

/**
 * 比賽列表用：若比賽打到決勝局，回傳決勝局比分。
 * record 為後端的比賽紀錄（a_games、b_games、match_format、games）。
 */
export function tiebreakScore(record) {
  if (!record.match_format) return null
  const max = maxGames(record.match_format)
  const aGames = record.a_games || 0
  const bGames = record.b_games || 0
  const played = aGames + bGames
  if (played < max - 1 || Math.abs(aGames - bGames) > 1) return null

  const gameNumber = Math.min(played, max)
  const game = record.games?.find(g => g.game === gameNumber)
  if (!game || (!game.a_score && !game.b_score)) return null
  return { aScore: game.a_score, bScore: game.b_score, gameNumber }
}
