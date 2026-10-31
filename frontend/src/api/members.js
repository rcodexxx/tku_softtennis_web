import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

export default {
  /** params：q、include_guests、include_inactive、organization_id、sort_by（roster 為校內優先）、sort_order、limit */
  list: params => apiClient.get('/members', { params }).then(unwrap),
  get: id => apiClient.get(`/members/${id}`).then(unwrap),
  stats: id => apiClient.get(`/members/${id}/stats`).then(unwrap),
  /** 球員頁：分數走勢、搭檔、對手、歷屆賽季；params：season_id（省略為目前賽季） */
  insights: (id, params) => apiClient.get(`/members/${id}/insights`, { params }).then(unwrap),
  /** 名單整理：校隊與校友會的隊員，status 為 team／alumni（已畢業）／left（已離隊）。 */
  roster: () => apiClient.get('/members/roster').then(unwrap),
  /** roster：[{ member_id, status }] */
  updateRoster: roster => apiClient.put('/members/roster', { roster }).then(unwrap),
  create: data => apiClient.post('/members', data).then(unwrap),
  update: (id, data) => apiClient.put(`/members/${id}`, data).then(unwrap),
  remove: id => apiClient.delete(`/members/${id}`),
  uploadAvatar: (id, file) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient
      .post(`/members/${id}/avatar`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
      .then(unwrap)
  },
  removeAvatar: id => apiClient.delete(`/members/${id}/avatar`).then(unwrap),
  /** 把這位球員的比賽併到 intoId，然後刪掉他（重複建立的訪客用）。 */
  merge: (id, intoId) => apiClient.post(`/members/${id}/merge`, { into_id: intoId }).then(unwrap)
}
