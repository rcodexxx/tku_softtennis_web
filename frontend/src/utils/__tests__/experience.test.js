import { expect, it } from 'vitest'
import { experienceIcon } from '../experience'

it('經驗等級對應後端的中文名稱', () => {
  expect(experienceIcon('資深')).toBe('⭐')
  expect(experienceIcon('中級')).toBe('🌳')
  expect(experienceIcon('unknown')).toBe('🌱')
})
