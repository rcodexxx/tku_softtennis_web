import apiClient from '@/services/apiClient'
import { unwrap, unwrapList } from './_helpers'

export default {
  /** params：season_id、scope、gender、include_guests、include_inactive、min_matches、sort_by、sort_order、page、per_page… */
  list: params => apiClient.get('/leaderboard', { params }).then(unwrapList),
  /** params：season_id（省略時為目前賽季） */
  statistics: params => apiClient.get('/leaderboard/statistics', { params }).then(unwrap),
  /** 組合榜；params：season_id、min_matches、sort_by（rating | chemistry） */
  pairs: params => apiClient.get('/leaderboard/pairs', { params }).then(unwrapList),
  compare: (memberId1, memberId2) => apiClient.get(`/leaderboard/compare/${memberId1}/${memberId2}`).then(unwrap)
}
