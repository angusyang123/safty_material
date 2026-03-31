import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// ==================== 物料管理 ====================
export const getMaterials = () => api.get('/materials')
export const reloadMaterials = () => api.post('/materials/reload')
export const getWarehouses = () => api.get('/warehouses')

// ==================== 预测数据管理 ====================

/**
 * 获取物料信息
 */
export const getMaterialInfo = (material) => {
  return api.get('/material/info', { params: { material } })
}

/**
 * 生成预测数据CSV
 * @param {string} warehouse - 仓库名称
 * @param {string} material - 物料名称
 * @param {number} initialStock - 初始库存(kg)
 * @param {number} predictDays - 预测天数
 * @param {string} startDate - 预测开始日期(YYYY-MM-DD)
 */
export const generatePrediction = (warehouse, material, initialStock = 2000, predictDays = 60, startDate = null) => {
  const params = {
    warehouse,
    material,
    initial_stock: initialStock,
    predict_days: predictDays
  }
  if (startDate) params.start_date = startDate
  return api.post('/prediction/generate', null, { params })
}

/**
 * 读取预测数据CSV
 */
export const readPrediction = (warehouse, material) => {
  return api.get('/prediction/read', { params: { warehouse, material } })
}

/**
 * 生成下单建议CSV
 */
export const generateOrder = (warehouse, material, initialStock = 2000, moq = null, leadtime = null) => {
  const params = {
    warehouse,
    material,
    initial_stock: initialStock
  }
  if (moq) params.moq = moq
  if (leadtime) params.leadtime = leadtime
  return api.post('/order/generate', null, { params })
}

/**
 * 读取下单建议CSV
 */
export const readOrder = (warehouse, material) => {
  return api.get('/order/read', { params: { warehouse, material } })
}

/**
 * 获取图表数据（历史+预测）
 */
export const getChartData = (warehouse, material, historyDays = 30) => {
  return api.get('/inventory/chart', {
    params: { warehouse, material, history_days: historyDays }
  })
}

// ==================== 兼容旧接口 ====================
export const getOverview = (initialStock) => {
  const params = initialStock ? { initial_stock: initialStock } : {}
  return api.get('/overview', { params })
}

export default api
