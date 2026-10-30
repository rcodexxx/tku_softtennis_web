<template>
  <div class="meter">
    <div class="meter-head">
      <span class="value num">{{ formatRating(rating) }}</span>
      <span class="status" :class="{ rated }">
        {{ rated ? '正式分數' : `評估中・${totalMatches ?? 0}/${RATED_MATCHES} 場` }}
      </span>
    </div>

    <div class="track" aria-hidden="true">
      <span class="fill" :style="{ width: `${ratingPercent(rating)}%` }"></span>
      <span class="marker" :style="{ left: `${ratingPercent(rating)}%` }"></span>
    </div>
    <div class="ticks num" aria-hidden="true">
      <span v-for="tick in TICKS" :key="tick">{{ tick }}</span>
    </div>

    <figure v-if="points.length > 1" class="trend">
      <figcaption>最近 {{ points.length }} 場表現</figcaption>
      <svg :viewBox="`0 0 ${WIDTH} ${HEIGHT}`" preserveAspectRatio="none" role="img" :aria-label="trendLabel">
        <line class="baseline" x1="0" :x2="WIDTH" :y1="y(rating)" :y2="y(rating)" />
        <polyline class="line" :points="points.map(p => `${p.x},${p.y}`).join(' ')" />
        <circle
          v-for="(point, index) in points"
          :key="index"
          class="dot"
          :class="{ above: point.value >= rating }"
          :cx="point.x"
          :cy="point.y"
          r="3.5"
          :style="{ '--i': index }"
        />
      </svg>
      <p class="trend-legend">
        <span class="legend-item"><span class="legend-line"></span>目前分數</span>
        <span class="legend-item"><span class="legend-dot above"></span>高於</span>
        <span class="legend-item"><span class="legend-dot"></span>低於</span>
      </p>
    </figure>

    <p class="hint">分數看局數表現：打得比預期好就上升，輸給強隊但比分接近也會加分。</p>
  </div>
</template>

<script setup>
  import { computed } from 'vue'
  import { formatRating, isRated, RATED_MATCHES, ratingPercent } from '@/utils/rating'

  const TICKS = [1, 4, 7, 10]
  const WIDTH = 300
  const HEIGHT = 72
  const PADDING = 8

  /** 分數、是否已打滿上榜場數，以及最近幾場的本場表現（舊到新，可省略）。 */
  const props = defineProps({
    rating: { type: Number, default: null },
    totalMatches: { type: Number, default: 0 },
    performances: { type: Array, default: () => [] }
  })

  const rated = computed(() => isRated(props.totalMatches))

  const range = computed(() => {
    const values = [...props.performances, props.rating].filter(v => typeof v === 'number')
    const low = Math.min(...values)
    const high = Math.max(...values)
    // 至少顯示 1 分的範圍，避免小波動被放大
    const pad = Math.max(0, 1 - (high - low)) / 2
    return { low: low - pad, high: high + pad }
  })

  const y = value =>
    PADDING + (1 - (value - range.value.low) / (range.value.high - range.value.low)) * (HEIGHT - PADDING * 2)

  const points = computed(() => {
    const values = props.performances.filter(v => typeof v === 'number')
    const step = values.length > 1 ? (WIDTH - PADDING * 2) / (values.length - 1) : 0
    return values.map((value, index) => ({ value, x: PADDING + index * step, y: y(value) }))
  })

  const trendLabel = computed(
    () => `最近 ${points.value.length} 場表現：${points.value.map(p => formatRating(p.value)).join('、')}`
  )
</script>

<style scoped>
  .meter-head {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 10px;
  }
  .value {
    font-size: 44px;
    font-weight: 700;
    line-height: 1;
    color: var(--blue-900);
  }
  .status {
    padding: 2px 10px;
    border-radius: var(--radius-full);
    background: var(--gold-100);
    color: #92400e;
    font-size: 12px;
    font-weight: 700;
  }
  .status.rated {
    background: var(--green-100);
    color: var(--green-600);
  }

  .track {
    position: relative;
    height: 12px;
    border-radius: var(--radius-full);
    background: var(--gray-100);
  }
  .fill {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, var(--blue-400), var(--blue-700));
    transform-origin: left;
    animation: grow 1s var(--ease-out) both 0.2s;
  }
  .marker {
    position: absolute;
    top: 50%;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #fff;
    border: 4px solid var(--blue-700);
    box-shadow: var(--shadow-md);
    transform: translate(-50%, -50%);
    animation: pop var(--duration-slow) var(--ease-spring) both 1s;
  }
  .ticks {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    font-size: 12px;
    color: var(--gray-400);
  }

  .trend {
    margin: 18px 0 0;
  }
  .trend figcaption {
    margin-bottom: 6px;
    font-size: 13px;
    font-weight: 700;
    color: var(--gray-700);
  }
  .trend svg {
    width: 100%;
    height: 72px;
    overflow: visible;
  }
  .baseline {
    stroke: var(--blue-200);
    stroke-width: 1.5;
    stroke-dasharray: 4 4;
    vector-effect: non-scaling-stroke;
  }
  .line {
    fill: none;
    stroke: var(--blue-500);
    stroke-width: 2;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
  }
  .dot {
    fill: var(--red-500);
    stroke: #fff;
    stroke-width: 1.5;
    animation: fade-in var(--duration-base) var(--ease-out) both;
    animation-delay: calc(var(--i) * 40ms + 300ms);
  }
  .dot.above {
    fill: var(--green-500);
  }
  .trend-legend {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    margin: 6px 0 0;
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .legend-line {
    width: 16px;
    border-top: 2px dashed var(--blue-200);
  }
  .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-right: 10px;
  }
  .legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--red-500);
  }
  .legend-dot.above {
    background: var(--green-500);
  }
  .hint {
    margin: 14px 0 0;
    font-size: 12px;
    color: var(--color-text-muted);
  }

  @keyframes grow {
    from {
      transform: scaleX(0);
    }
  }
  @keyframes pop {
    from {
      transform: translate(-50%, -50%) scale(0);
    }
  }
  @keyframes fade-in {
    from {
      opacity: 0;
    }
  }
</style>
