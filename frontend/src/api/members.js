import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

export default {
  /** params：q、include_guests、include_inactive、organization_id、sort_by、sort_order、limit */
  list: params => apiClient.get('/members', { params }).then(unwrap),
  get: id => apiClient.get(`/members/${id}`).then(unwrap),
  stats: id => apiClient.get(`/members/${id}/stats`).then(unwrap),
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
  removeAvatar: id => apiClient.delete(`/members/${id}/avatar`).then(unwrap)
}
