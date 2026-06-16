import service, { requestWithRetry } from './index'

/**
 * 列出角色（用户库）
 * @param {Object} params - { q?, tag?, enabled?, limit?, offset? }
 */
export const listCharacters = (params = {}) => {
  return service.get('/api/characters/list', { params })
}

/**
 * 获取单个角色
 * @param {string} characterId
 */
export const getCharacter = (characterId) => {
  return service.get(`/api/characters/${characterId}`)
}

/**
 * 创建角色
 * @param {Object} data
 */
export const createCharacter = (data) => {
  return requestWithRetry(() => service.post('/api/characters/create', data), 2, 800)
}

/**
 * 更新角色
 * @param {string} characterId
 * @param {Object} data
 */
export const updateCharacter = (characterId, data) => {
  return service.put(`/api/characters/${characterId}`, data)
}

/**
 * 删除角色
 * @param {string} characterId
 */
export const deleteCharacter = (characterId) => {
  return service.delete(`/api/characters/${characterId}`)
}

/**
 * 批量导入角色（上传 CSV/JSON 文件）
 * @param {File} file
 */
export const importCharactersFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return service.post('/api/characters/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 批量导入角色（直接传 JSON 数组或 CSV 文本）
 * @param {Object} payload - { characters?: [], csv?: '' }
 */
export const importCharactersData = (payload) => {
  return service.post('/api/characters/import', payload)
}

/**
 * 导出全部角色为 JSON 文件（触发浏览器下载）
 */
export const exportCharactersUrl = () => {
  const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001'
  return `${base}/api/characters/export`
}
