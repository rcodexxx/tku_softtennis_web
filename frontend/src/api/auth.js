import apiClient from '@/services/apiClient'
import { unwrap } from './_helpers'

export default {
  login: credentials => apiClient.post('/auth/login', credentials).then(unwrap),
  register: phoneNumber => apiClient.post('/auth/register', { phone_number: phoneNumber }).then(unwrap),
  me: () => apiClient.get('/auth/me').then(unwrap),
  refresh: refreshToken =>
    apiClient.post('/auth/refresh', null, { headers: { Authorization: `Bearer ${refreshToken}` } }).then(unwrap),
  changePassword: (oldPassword, newPassword) =>
    apiClient.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }).then(unwrap)
}
