import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

export default {
  list: () => apiClient.get('/organizations').then(unwrap),
  get: id => apiClient.get(`/organizations/${id}`).then(unwrap),
  create: data => apiClient.post('/organizations', data).then(unwrap),
  update: (id, data) => apiClient.put(`/organizations/${id}`, data).then(unwrap),
  remove: id => apiClient.delete(`/organizations/${id}`)
}
