export function organizationLabel(member) {
  return member?.organization ? member.organization.short_name || member.organization.name : ''
}
