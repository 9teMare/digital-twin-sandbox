const DEFAULT_LABELS = new Set(['Entity', 'Node'])

const ENTITY_PERSON_TERMS = [
  'person',
  'user',
  'participant',
  'customer',
  'member',
  'account',
  'profile',
  'persona',
  'trader',
  'investor',
  'influencer',
  'creator',
  'student',
  'professor',
  'official',
  'executive',
  'ceo',
  'founder',
  'employee',
  'journalist',
  'celebrity',
  'lawyer',
  'doctor',
  'alumni',
  'expert',
  'faculty'
]

const ENTITY_NON_PERSON_TERMS = [
  'campaigncreator',
  'campaign_creator',
  'date',
  'time',
  'timestamp',
  'version',
  'uid',
  'uuid',
  'id',
  'hash',
  'code',
  'field',
  'config',
  'parameter',
  'metric',
  'score',
  'rate',
  'count',
  'registration',
  'register',
  'signup',
  'deposit',
  'transaction',
  'trading',
  'trade',
  'task',
  'reward',
  'step',
  'status',
  'language',
  'risk',
  'channel',
  'property'
]

const FIXED_GROUP_COLORS = {
  Entity: '#FF6B35',
  Organization: '#004E89',
  CampaignCreator: '#7B2D8E',
  People: '#1A936F'
}

const OTHER_TYPE_COLORS = [
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

const normalizeText = (value) => String(value || '').toLowerCase()

const flattenAttributes = (attributes = {}) => (
  Object.entries(attributes)
    .flatMap(([key, value]) => [key, value])
    .filter(value => value !== null && value !== undefined)
    .map(value => String(value))
)

const buildSearchText = (node) => {
  const parts = [
    node?.name,
    node?.summary,
    ...flattenAttributes(node?.attributes || {})
  ]

  return normalizeText(parts.filter(Boolean).join(' '))
}

const includesTerm = (text, term) => {
  const normalizedTerm = normalizeText(term)
  const compactText = text.replace(/[^a-z0-9]+/g, '')
  const compactTerm = normalizedTerm.replace(/[^a-z0-9]+/g, '')

  return text.includes(normalizedTerm) || compactText.includes(compactTerm)
}

const isPureEntityPerson = (node) => {
  const text = buildSearchText(node)

  if (!text) {
    return false
  }

  if (ENTITY_NON_PERSON_TERMS.some(term => includesTerm(text, term))) {
    return false
  }

  return ENTITY_PERSON_TERMS.some(term => includesTerm(text, term))
}

export const getSpecificType = (labels = []) => (
  labels.find(label => label && !DEFAULT_LABELS.has(label)) || 'Entity'
)

export const getVisualGroup = (specificType, node = null) => {
  const normalized = normalizeType(specificType)

  if (!normalized || normalized === 'entity') {
    return isPureEntityPerson(node) ? 'People' : 'Entity'
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
  const visualGroup = getVisualGroup(specificType, node)

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
