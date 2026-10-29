<template>
  <n-collapse class="rating-guide">
    <n-collapse-item title="評分系統怎麼算？" name="guide">
      <div class="guide-grid">
        <section>
          <h4>排名分數</h4>
          <p>
            採用 TrueSkill 評分。每位球員有實力估計 μ 與不確定性 σ，排名分數為
            <code>(μ − 2σ) × 100</code>：比賽越少、σ 越大，分數就越保守，避免新手打一兩場就衝上前段。
          </p>
        </section>
        <section>
          <h4>比賽如何影響分數</h4>
          <p>
            贏球加分、輸球扣分；贏過分數比自己高的對手加得更多。比分差距越大，分數變動也越大。混合性別的比賽另有加減分調整。
          </p>
        </section>
        <section>
          <h4>穩定度與可信度</h4>
          <p>都由 σ 換算成 0–100%：σ 越小代表系統越確定你的實力，打越多場比賽就會越高。</p>
        </section>
        <section>
          <h4>經驗等級</h4>
          <ul class="levels">
            <li v-for="(level, index) in EXPERIENCE_LEVELS" :key="level.label">
              {{ level.icon }} {{ level.label }}
              <span class="range">{{ sigmaRange(index) }}</span>
            </li>
          </ul>
        </section>
      </div>
    </n-collapse-item>
  </n-collapse>
</template>

<script setup>
  import { EXPERIENCE_LEVELS } from '@/utils/experience'

  const sigmaRange = index => {
    const low = EXPERIENCE_LEVELS[index].minSigma.toFixed(1)
    if (index === 0) return `σ ≥ ${low}`
    return `${low} ≤ σ < ${EXPERIENCE_LEVELS[index - 1].minSigma.toFixed(1)}`
  }
</script>

<style scoped>
  .rating-guide {
    padding: 4px 20px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
  }
  .guide-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px 28px;
  }
  h4 {
    margin: 0 0 6px;
    color: var(--blue-900);
  }
  p {
    margin: 0;
    line-height: 1.7;
    color: var(--gray-700);
  }
  code {
    padding: 1px 6px;
    border-radius: 6px;
    background: var(--blue-50);
    color: var(--blue-700);
    font-weight: 700;
  }
  .levels {
    margin: 0;
    padding: 0;
    list-style: none;
    display: grid;
    gap: 4px;
  }
  .range {
    margin-left: 6px;
    font-size: 12px;
    color: var(--color-text-muted);
  }
  @media (max-width: 720px) {
    .guide-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
