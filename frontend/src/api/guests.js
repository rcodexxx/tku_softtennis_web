import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

export default {
  /** 目前使用者建立的訪客；params：q、guest_role、organization_id、limit */
  search: params => apiClient.get('/guests', { params }).then(unwrap),
  roleOptions: () => apiClient.get('/guests/role-options').then(unwrap),
  create: data => apiClient.post('/guests', data).then(unwrap),
  update: (id, data) => apiClient.put(`/guests/${id}`, data).then(unwrap),
  remove: id => apiClient.delete(`/guests/${id}`)
}
