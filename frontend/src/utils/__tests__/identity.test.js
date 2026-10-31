import { describe, expect, it } from 'vitest'
import { guessFromStudentId } from '../identity'

describe('guessFromStudentId', () => {
  it('reads programme and enrolment year', () => {
    expect(guessFromStudentId('413630152')).toEqual({ study_program: 'bachelor', enrolled_year: 113 })
    expect(guessFromStudentId('611460162')).toEqual({ study_program: 'master', enrolled_year: 111 })
  })

  it('leaves unknown formats alone', () => {
    expect(guessFromStudentId('710270033')).toBeNull()
    expect(guessFromStudentId('')).toBeNull()
    expect(guessFromStudentId(null)).toBeNull()
  })
})
