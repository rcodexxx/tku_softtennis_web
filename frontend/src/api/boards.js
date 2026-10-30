import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

/** 自訂榜單（例如「打球嗎」），目前只有幹部能用。 */
export default {
  list: () => apiClient.get('/boards').then(unwrap),
  /** data：{ name, member_ids } */
  create: data => apiClient.post('/boards', data).then(unwrap),
  update: (id, data) => apiClient.put(`/boards/${id}`, data).then(unwrap),
  remove: id => apiClient.delete(`/boards/${id}`)
}
