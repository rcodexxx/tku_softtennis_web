const GRID = 5
const HALF = Math.ceil(GRID / 2)
// 對應 tokens.css 的 --avatar-0 到 --avatar-7（淺色、深色各有一組）
export const AVATAR_TONES = 8

/** FNV-1a：把字串轉成 32 位元的雜湊值。 */
function hash(text) {
  let value = 0x811c9dc5
  for (const char of text) {
    value ^= char.codePointAt(0)
    value = Math.imul(value, 0x01000193) >>> 0
  }
  return value
}

/** mulberry32：用雜湊值當種子的亂數，確保同一個人每次產生的圖案都一樣。 */
function random(seed) {
  let state = seed
  return () => {
    state = (state + 0x6d2b79f5) >>> 0
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/**
 * GitHub 風格的預設頭像：5×5 左右對稱的方塊圖案。
 * 回傳 { tone, cells }：tone 是主題色票的編號，cells 是要上色的 [x, y] 格子。
 */
export function identicon(seed) {
  const next = random(hash(String(seed ?? '')))
  const tone = Math.floor(next() * AVATAR_TONES)
  const cells = []
  for (let y = 0; y < GRID; y++) {
    for (let x = 0; x < HALF; x++) {
      if (next() < 0.5) continue
      cells.push([x, y])
      if (x !== GRID - 1 - x) cells.push([GRID - 1 - x, y])
    }
  }
  // 太空的圖案看不出差別，至少補上中間一列
  if (cells.length < 4) {
    for (let y = 1; y < GRID - 1; y++) cells.push([HALF - 1, y])
  }
  return { tone, cells }
}
