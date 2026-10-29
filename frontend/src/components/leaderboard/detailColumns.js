import { h } from 'vue'
import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
import { experienceIcon, EXPERIENCE_LEVELS } from '@/utils/experience'
import RecentForm from './RecentForm.vue'
import ScoreChange from './ScoreChange.vue'

const bar = (value, color) =>
  h('div', { class: 'cell-bar' }, [
    h('span', { class: 'cell-bar-track' }, [
      h('span', { class: 'cell-bar-fill', style: { width: `${value}%`, background: color } })
    ]),
    h('span', { class: 'num cell-bar-text' }, `${Math.round(value)}%`)
  ])

const numberSorter = key => (a, b) => a[key] - b[key]
const experienceRank = level => EXPERIENCE_LEVELS.findIndex(item => item.label === level)

/** 詳細數據表格的欄位（排序在前端進行）。 */
export function detailColumns() {
  return [
    {
      title: '#',
      key: 'rank',
      width: 64,
      align: 'center',
      sorter: numberSorter('rank'),
      render: row => h('span', { class: ['num', 'cell-rank', row.rank <= 3 && `top-${row.rank}`] }, row.rank)
    },
    {
      title: '球員',
      key: 'name',
      minWidth: 180,
      render: row =>
        h('div', { class: 'cell-player' }, [
          h(PlayerAvatar, { id: row.id, name: row.name, src: row.avatar_url, size: 36 }),
          h('div', { class: 'cell-player-text' }, [
            h('span', { class: 'cell-player-name' }, [
              row.name,
              row.is_guest && h('span', { class: 'guest-tag' }, '訪客')
            ]),
            h('span', { class: 'cell-player-sub' }, row.organization_name || '—')
          ])
        ])
    },
    {
      title: '排名分數',
      key: 'conservative_score',
      width: 130,
      align: 'right',
      sorter: numberSorter('conservative_score'),
      render: row =>
        h('div', { class: 'cell-score' }, [
          h('span', { class: 'num cell-score-value' }, Math.round(row.conservative_score * 100)),
          h(ScoreChange, { change: row.score_change })
        ])
    },
    {
      title: '潛在實力',
      key: 'mu',
      width: 100,
      align: 'right',
      sorter: numberSorter('mu'),
      render: row => h('span', { class: 'num cell-number' }, Math.round(row.mu * 100))
    },
    {
      title: '勝率',
      key: 'win_rate',
      width: 150,
      sorter: numberSorter('win_rate'),
      render: row => bar(row.win_rate, 'linear-gradient(90deg, var(--blue-400), var(--blue-600))')
    },
    {
      title: '穩定度',
      key: 'consistency_rating',
      width: 150,
      sorter: numberSorter('consistency_rating'),
      render: row => bar(row.consistency_rating, 'linear-gradient(90deg, #4ade80, var(--green-600))')
    },
    {
      title: '經驗',
      key: 'experience_level',
      width: 90,
      sorter: (a, b) => experienceRank(a.experience_level) - experienceRank(b.experience_level),
      render: row => `${experienceIcon(row.experience_level)} ${row.experience_level}`
    },
    {
      title: '戰績',
      key: 'total_matches',
      width: 100,
      align: 'center',
      sorter: numberSorter('total_matches'),
      render: row =>
        h('span', { class: 'num cell-record' }, [
          h('b', { class: 'win' }, row.wins),
          ' - ',
          h('b', { class: 'loss' }, row.losses)
        ])
    },
    { title: '近況', key: 'recent_form', width: 140, render: row => h(RecentForm, { form: row.recent_form }) }
  ]
}
