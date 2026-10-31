import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

/** 練習日：到場名單、排下一輪、當天戰報（get 會帶 summary）。 */
export default {
  list: () => apiClient.get('/practice-sessions').then(unwrap),
  get: id => apiClient.get(`/practice-sessions/${id}`).then(unwrap),
  /** data：{ session_date, location, notes, player_ids } */
  create: data => apiClient.post('/practice-sessions', data).then(unwrap),
  update: (id, data) => apiClient.put(`/practice-sessions/${id}`, data).then(unwrap),
  remove: id => apiClient.delete(`/practice-sessions/${id}`),
  /** params：{ courts, mode: 'rotate' | 'balanced', seed } */
  nextRound: (id, params) => apiClient.get(`/practice-sessions/${id}/next-round`, { params }).then(unwrap)
}
