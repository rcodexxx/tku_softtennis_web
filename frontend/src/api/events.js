import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

export default {
  list: () => apiClient.get('/events').then(unwrap),
  get: id => apiClient.get(`/events/${id}`).then(unwrap),
  /** data：{ name, start_date, end_date, location, notes, counts_toward_rating } */
  create: data => apiClient.post('/events', data).then(unwrap),
  update: (id, data) => apiClient.put(`/events/${id}`, data).then(unwrap),
  remove: id => apiClient.delete(`/events/${id}`)
}
