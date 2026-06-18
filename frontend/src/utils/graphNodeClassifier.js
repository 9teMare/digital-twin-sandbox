const DEFAULT_LABELS = new Set(['Entity', 'Node'])

const PEOPLE_TYPES = new Set([
  'person',
  'campaigncreator',
  'user',
  'participant',
  'creator',
  'influencer',
  'student',
  'professor',
  'official',
  'executive',
  'customer',
  'ceo',
  'founder',
  'employee',
  'journalist',
  'celebrity',
  'lawyer',
  'doctor',
  'alumni',
  'expert',
  'faculty',
  'trader',
  'investor'
])

const ORGANIZATION_TYPES = new Set([
  'organization',
  'company',
  'university',
  'governmentagency',
  'mediaoutlet',
  'hospital',
  'school',
  'ngo',
  'nonprofit',
  'platform',
  'socialmediaplatform',
  'community',
  'association',
  'group',
  'team'
])

const FIXED_GROUP_COLORS = {
  People: '#1A936F',
  Organization: '#004E89',
  Entity: '#FF6B35'
}

const OTHER_TYPE_COLORS = [
  '#7B2D8E',
  '#C5283D',
  '#E9724C',
  '#3498db',
  '#9b59b6',
  '#27ae60',
  '#f39c12',
  '#2D3436',
  '#6C5CE7'
]

const normalizeType = (type) => String(type || '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase()

export const getSpecificType = (labels = []) => (
  labels.find(label => label && !DEFAULT_LABELS.has(label)) || 'Entity'
)

export const getVisualGroup = (specificType) => {
  const normalized = normalizeType(specificType)

  if (!normalized || normalized === 'entity') {
    return 'Entity'
  }

  if (
    PEOPLE_TYPES.has(normalized) ||
    normalized.endsWith('person') ||
    normalized.endsWith('user') ||
    normalized.endsWith('creator') ||
    normalized.endsWith('participant') ||
    normalized.endsWith('customer') ||
    normalized.endsWith('influencer')
  ) {
    return 'People'
  }

  if (
    ORGANIZATION_TYPES.has(normalized) ||
    normalized.endsWith('organization') ||
    normalized.endsWith('company') ||
    normalized.endsWith('agency') ||
    normalized.endsWith('institution') ||
    normalized.endsWith('platform') ||
    normalized.endsWith('community') ||
    normalized.endsWith('group')
  ) {
    return 'Organization'
  }

  return specificType || 'Entity'
}

export const getVisualGroupColor = (visualGroup, index = 0) => {
  if (FIXED_GROUP_COLORS[visualGroup]) {
    return FIXED_GROUP_COLORS[visualGroup]
  }
  return OTHER_TYPE_COLORS[index % OTHER_TYPE_COLORS.length]
}

export const classifyGraphNode = (node) => {
  const specificType = getSpecificType(node?.labels || [])
  const visualGroup = getVisualGroup(specificType)

  return {
    specificType,
    visualGroup
  }
}

export const buildEntityTypeLegend = (nodes = []) => {
  const typeMap = {}

  nodes.forEach(node => {
    const { visualGroup } = classifyGraphNode(node)
    if (!typeMap[visualGroup]) {
      const colorIndex = Object.keys(typeMap)
        .filter(type => !FIXED_GROUP_COLORS[type])
        .length

      typeMap[visualGroup] = {
        name: visualGroup,
        count: 0,
        color: getVisualGroupColor(visualGroup, colorIndex)
      }
    }
    typeMap[visualGroup].count++
  })

  return Object.values(typeMap)
}
