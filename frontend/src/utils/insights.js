/** 至少要打過這麼多場，才拿來挑最佳搭檔、剋星、苦主。 */
export const MIN_HEAD_TO_HEAD = 2

/**
 * 從搭檔與對手戰績挑出亮點：
 * - bestPartner：勝率最高的搭檔
 * - nemesis（剋星）：對上勝率最低、且輸多贏少的對手
 * - favorite（苦主）：對上勝率最高、且贏多輸少的對手
 */
export function headToHeadHighlights(partners = [], opponents = [], minMatches = MIN_HEAD_TO_HEAD) {
  const enough = list => list.filter(entry => entry.matches >= minMatches)
  const byRate = (a, b) => b.win_rate - a.win_rate || b.matches - a.matches
  const partnersRanked = enough(partners).sort(byRate)
  const opponentsRanked = enough(opponents).sort(byRate)
  const nemesis = opponentsRanked.at(-1)
  const favorite = opponentsRanked[0]
  return {
    bestPartner: partnersRanked[0] ?? null,
    nemesis: nemesis && nemesis.win_rate < 50 ? nemesis : null,
    favorite: favorite && favorite.win_rate > 50 ? favorite : null
  }
}
