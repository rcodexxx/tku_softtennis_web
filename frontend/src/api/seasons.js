import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

export default {
  /** 所有賽季，最新的在前；目前賽季的 is_current 為 true。 */
  list: () => apiClient.get('/seasons').then(unwrap),
  /** data：{ name, start_date, roster: [{ member_id, status: 'team' | 'alumni' | 'left' }] } */
  create: data => apiClient.post('/seasons', data).then(unwrap)
}
