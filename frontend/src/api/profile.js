import apiClient from '@/services/apiClient'
import { unwrap, unwrapList } from './_helpers'

export default {
  get: () => apiClient.get('/profile/me').then(unwrap),
  update: data => apiClient.put('/profile/me', data).then(unwrap),
  matches: params => apiClient.get('/profile/me/matches', { params }).then(unwrapList)
}
