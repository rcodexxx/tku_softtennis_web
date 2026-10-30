<template>
  <n-collapse class="rating-guide">
    <n-collapse-item title="分數怎麼算？" name="guide">
      <div class="guide-grid">
        <section>
          <h4>分數 1–10</h4>
          <p>
            分數是<b>這個賽季最近 20 場「本場表現」的平均</b>，越近的比賽越重要。每個賽季重新開始：男生 5.0、女生
            4.0，甲組再加 1 分。
          </p>
        </section>
        <section>
          <h4>本場表現</h4>
          <p>
            先用兩隊分數算出<b>預期拿下幾成局數</b>：差 1 分時，強隊預期拿 7
            成。實際打得比預期好，本場表現就高於你目前的分數； 比預期差就低於。同隊兩人加減一樣多，單場最多 ±1.5 分。
          </p>
        </section>
        <section>
          <h4>看局數，不只看輸贏</h4>
          <p>
            4-0 比 4-3 加得多；輸給強很多的隊伍但比分接近，<b>輸了也會加分</b>。所以男女混打時，
            女生只要打得比預期好就會進步，不用一定要贏。
          </p>
        </section>
        <section>
          <h4>範例</h4>
          <p>
            你的隊伍 <code>4.0</code> 對上 <code>5.0</code>，預期只拿 3 成局數。結果 3-4 惜敗（拿到 4 成多），
            本場表現比你目前的分數高約 <code>0.7</code>。
          </p>
        </section>
      </div>
    </n-collapse-item>
  </n-collapse>
</template>

<script setup></script>

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
  @media (max-width: 720px) {
    .guide-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
