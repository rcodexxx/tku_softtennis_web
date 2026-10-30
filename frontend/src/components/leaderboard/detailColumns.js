import { h } from 'vue'
import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
import { formatDate } from '@/utils/format'
import { formatRating, isRated } from '@/utils/rating'
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
      title: '分數',
      key: 'rating',
      width: 130,
      align: 'right',
      sorter: numberSorter('rating'),
      render: row =>
        h('div', { class: 'cell-score' }, [
          h('span', { class: 'num cell-score-value' }, formatRating(row.rating)),
          isRated(row.total_matches)
            ? h(ScoreChange, { change: row.score_change })
            : h('span', { class: 'cell-provisional' }, '評估中')
        ])
    },
    {
      title: '勝率',
      key: 'win_rate',
      width: 150,
      sorter: numberSorter('win_rate'),
      render: row => bar(row.win_rate, 'linear-gradient(90deg, var(--blue-400), var(--blue-600))')
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
    { title: '近況', key: 'recent_form', width: 140, render: row => h(RecentForm, { form: row.recent_form }) },
    {
      title: '最近比賽',
      key: 'last_match_date',
      width: 120,
      sorter: (a, b) => (a.last_match_date || '').localeCompare(b.last_match_date || ''),
      render: row => h('span', { class: 'num cell-number' }, formatDate(row.last_match_date) || '—')
    }
  ]
}
