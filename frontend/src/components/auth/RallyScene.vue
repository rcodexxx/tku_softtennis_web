<template>
  <figure class="rally" aria-hidden="true">
    <div class="hud">
      <span class="hud-label">Rally</span>
      <span class="count num">{{ String(hits).padStart(3, '0') }}</span>
    </div>
    <svg viewBox="0 0 400 240" xmlns="http://www.w3.org/2000/svg">
      <!-- 球場：地面、發球線刻度、網子 -->
      <line class="ground" x1="10" y1="200" x2="390" y2="200" />
      <path class="tick" d="M60 200v6M140 200v6M260 200v6M340 200v6" />
      <line class="post" x1="200" y1="200" x2="200" y2="160" />
      <path class="mesh" d="M200 164h0M196 168h8M196 176h8M196 184h8M196 192h8" />
      <line class="tape" x1="194" y1="162" x2="206" y2="162" />

      <!-- 球的影子 -->
      <ellipse class="shadow" :cx="ball.x" cy="203" :rx="shadowSize" :ry="shadowSize / 4" />

      <!-- 兩位球員：左邊的正面，右邊的鏡像 -->
      <g v-for="player in players" :key="player.side" :transform="player.transform">
        <g :transform="`translate(0 ${player.bob})`">
          <circle class="body" cx="0" cy="-74" r="7" />
          <path class="body" d="M0 -66 L-2 -36 M-2 -36 L-12 -4 M-2 -36 L8 -4 M0 -58 L-12 -44" />
          <!-- 揮拍的手臂：以肩膀為軸轉動 -->
          <g :transform="`rotate(${player.swing} 0 -60)`">
            <path class="body" d="M0 -60 L16 -52" />
            <path class="racket" d="M16 -52 L26 -46" />
            <ellipse class="racket" cx="33" cy="-42" rx="6" ry="8.5" transform="rotate(-60 33 -42)" />
          </g>
        </g>
      </g>

      <!-- 軟式網球：白色橡膠球加紅色標記 -->
      <g :transform="`translate(${ball.x} ${ball.y}) rotate(${ball.spin})`">
        <circle class="ball" r="5" />
        <rect class="ball-mark" x="-1" y="-2.6" width="4.4" height="1.8" rx="0.9" />
      </g>
    </svg>
  </figure>
</template>

<script setup>
  import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

  // 一個來回：左邊擊球 → 右場落地 → 右邊擊球 → 左場落地 → 回到左邊擊球（座標是 viewBox）
  const LEFT_HIT = { x: 98, y: 150 }
  const RIGHT_HIT = { x: 302, y: 150 }
  const SEGMENTS = [
    { from: LEFT_HIT, control: { x: 205, y: 30 }, to: { x: 280, y: 200 }, ms: 900 },
    { from: { x: 280, y: 200 }, control: { x: 292, y: 150 }, to: RIGHT_HIT, ms: 380, hitBy: 'right' },
    { from: RIGHT_HIT, control: { x: 195, y: 30 }, to: { x: 120, y: 200 }, ms: 900 },
    { from: { x: 120, y: 200 }, control: { x: 108, y: 150 }, to: LEFT_HIT, ms: 380, hitBy: 'left' }
  ]
  const CYCLE = SEGMENTS.reduce((sum, segment) => sum + segment.ms, 0)
  const SWING_MS = 260

  const ball = reactive({ x: LEFT_HIT.x, y: LEFT_HIT.y, spin: 0 })
  const hits = ref(0)
  const lastHit = reactive({ left: -Infinity, right: -Infinity })
  const now = ref(0)
  let frame = null
  let start = null
  let lastSegment = -1

  const bezier = (a, c, b, t) => (1 - t) ** 2 * a + 2 * (1 - t) * t * c + t ** 2 * b
  const shadowSize = computed(() => 3 + (ball.y / 200) * 7)

  // 擊球後的揮拍：快速往前再慢慢收回
  const swingAngle = side => {
    const since = now.value - lastHit[side]
    if (since < 0 || since > SWING_MS * 2) return 18
    const p = since / (SWING_MS * 2)
    return 18 - 70 * Math.sin(Math.PI * Math.min(1, p * 1.4))
  }
  const players = computed(() => [
    { side: 'left', transform: 'translate(78 200)', swing: swingAngle('left'), bob: Math.sin(now.value / 260) * 1.5 },
    {
      side: 'right',
      transform: 'translate(322 200) scale(-1 1)',
      swing: swingAngle('right'),
      bob: Math.sin(now.value / 260 + 1.5) * 1.5
    }
  ])

  const tick = timestamp => {
    if (start === null) start = timestamp
    now.value = timestamp
    let elapsed = (timestamp - start) % CYCLE
    let index = 0
    while (elapsed > SEGMENTS[index].ms) {
      elapsed -= SEGMENTS[index].ms
      index += 1
    }
    const segment = SEGMENTS[index]
    const t = elapsed / segment.ms
    ball.x = bezier(segment.from.x, segment.control.x, segment.to.x, t)
    ball.y = bezier(segment.from.y, segment.control.y, segment.to.y, t)
    ball.spin = (timestamp / 3) % 360

    // 進入下一段時，如果上一段結束在球拍上就算一次擊球
    if (index !== lastSegment) {
      const finished = SEGMENTS[(index + SEGMENTS.length - 1) % SEGMENTS.length]
      if (lastSegment !== -1 && finished.hitBy) {
        lastHit[finished.hitBy] = timestamp
        hits.value += 1
      }
      lastSegment = index
    }
    frame = requestAnimationFrame(tick)
  }

  onMounted(() => {
    // 不喜歡動畫的人看靜止畫面
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return
    frame = requestAnimationFrame(tick)
  })
  onBeforeUnmount(() => cancelAnimationFrame(frame))
</script>

<style scoped>
  .rally {
    position: relative;
    width: 100%;
    max-width: 520px;
    margin: 0;
  }
  .hud {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
    align-items: baseline;
    gap: 10px;
  }
  .hud .hud-label {
    color: color-mix(in srgb, var(--bg) 60%, transparent);
  }
  .count {
    font-size: 28px;
    color: var(--accent);
  }
  svg {
    display: block;
    width: 100%;
    overflow: visible;
  }
  .ground {
    stroke: color-mix(in srgb, var(--bg) 70%, transparent);
    stroke-width: 1.5;
  }
  .tick,
  .mesh {
    stroke: color-mix(in srgb, var(--bg) 35%, transparent);
    stroke-width: 1;
  }
  .post {
    stroke: color-mix(in srgb, var(--bg) 70%, transparent);
    stroke-width: 2;
  }
  .tape {
    stroke: var(--bg);
    stroke-width: 2;
  }
  .shadow {
    fill: color-mix(in srgb, var(--bg) 20%, transparent);
  }
  .body {
    fill: none;
    stroke: var(--bg);
    stroke-width: 3;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .racket {
    fill: none;
    stroke: var(--accent);
    stroke-width: 2.4;
    stroke-linecap: round;
  }
  .ball {
    fill: #ffffff;
  }
  .ball-mark {
    fill: #e8483a;
  }
</style>
