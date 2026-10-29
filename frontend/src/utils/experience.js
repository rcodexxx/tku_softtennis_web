// 與後端 domain/rating.py 的 EXPERIENCE_LEVELS 對應（sigma 由大到小）
export const EXPERIENCE_LEVELS = [
  { label: '新手', icon: '🌱', minSigma: 7.0 },
  { label: '初級', icon: '🌿', minSigma: 5.0 },
  { label: '中級', icon: '🌳', minSigma: 3.0 },
  { label: '高級', icon: '💫', minSigma: 2.0 },
  { label: '資深', icon: '⭐', minSigma: 0 }
]

export function experienceIcon(level) {
  return EXPERIENCE_LEVELS.find(item => item.label === level)?.icon || '🌱'
}
