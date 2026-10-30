import apiClient from '@/services/apiClient'
import { unwrap, unwrapList } from './_helpers'

export default {
  /** params：page、per_page、sort_by、sort_order、start_date、end_date、category、event_id、match_type、match_format、player_ids、result */
  list: params => apiClient.get('/match-records', { params }).then(unwrapList),
  get: id => apiClient.get(`/match-records/${id}`).then(unwrap),
  create: data => apiClient.post('/match-records', data).then(unwrap),
  /** 一次建立多場；任何一場有錯就全部不寫入，錯誤在 details.records[第幾筆] */
  createBatch: records => apiClient.post('/match-records/batch', { records }).then(unwrap),
  update: (id, data) => apiClient.put(`/match-records/${id}`, data).then(unwrap),
  remove: id => apiClient.delete(`/match-records/${id}`)
}
