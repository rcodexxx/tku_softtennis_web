import apiClient from '@/services/apiClient'
import { unwrap, unwrapList } from './_helpers'

export default {
  /** params：include_guests、include_inactive、min_matches、sort_by、sort_order、page、per_page… */
  list: params => apiClient.get('/leaderboard', { params }).then(unwrapList),
  statistics: () => apiClient.get('/leaderboard/statistics').then(unwrap),
  compare: (memberId1, memberId2) => apiClient.get(`/leaderboard/compare/${memberId1}/${memberId2}`).then(unwrap)
}
