const AVATAR_COLORS = ['#18a058', '#2080f0', '#f0a020', '#d03050', '#7c3aed', '#06b6d4', '#10b981', '#f59e0b']

export function playerColor(playerId) {
  return playerId ? AVATAR_COLORS[playerId % AVATAR_COLORS.length] : '#f0f0f0'
}

export function playerInitial(name) {
  if (!name || name === '未知球員') return '?'
  return name.charAt(0).toUpperCase()
}

export function organizationLabel(member) {
  return member?.organization ? member.organization.short_name || member.organization.name : ''
}
