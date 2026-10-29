import confetti from 'canvas-confetti'

const COLORS = ['#f2b705', '#ffd95a', '#163a80', '#e5383f', '#ffffff']
let fire = null

/** 灑彩帶。不用 Web Worker：有些瀏覽器環境的 OffscreenCanvas 不完整。 */
export function celebrate(options = {}) {
  if (!fire) {
    const canvas = document.createElement('canvas')
    Object.assign(canvas.style, {
      position: 'fixed',
      inset: '0',
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      zIndex: 3000
    })
    document.body.appendChild(canvas)
    fire = confetti.create(canvas, { resize: true, useWorker: false })
  }
  return fire({ particleCount: 90, spread: 75, startVelocity: 38, origin: { y: 0.35 }, colors: COLORS, ...options })
}
