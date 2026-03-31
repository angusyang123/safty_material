<template>
  <div class="detail-page" v-loading="loading">
    <div class="header">
      <el-button @click="goBack">← 返回总览</el-button>
      <h2>{{ warehouse }} - {{ material }}</h2>
      <el-tag v-if="predictionSummary.total_days" type="success">
        已预测 {{ predictionSummary.total_days }} 天
      </el-tag>
    </div>

    <!-- 参数设置区 -->
    <el-card class="param-card">
      <template #header>
        <div class="card-header">
          <span>参数设置</span>
          <div class="action-buttons">
            <el-button type="primary" @click="handleGeneratePrediction" :loading="loading">
              生成预测
            </el-button>
            <el-button
              type="warning"
              @click="handleReloadPrediction"
              :loading="loading"
              :disabled="!predictionFileExists"
            >
              重新加载预测
            </el-button>
            <el-button
              type="success"
              @click="handleGenerateOrder"
              :loading="loading"
              :disabled="!predictionData.length"
            >
              生成下单建议
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="4">
          <div class="param-item">
            <span class="label">初始库存:</span>
            <el-input-number
              v-model="initialStock"
              :min="0"
              :step="100"
              controls-position="right"
              :precision="0"
            />
            <span class="unit">kg</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="param-item">
            <span class="label">预测天数:</span>
            <el-input-number
              v-model="predictDays"
              :min="1"
              :max="365"
              controls-position="right"
              :precision="0"
            />
            <span class="unit">天</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="param-item">
            <span class="label">MOQ:</span>
            <span class="value readonly">{{ materialInfo.moq }} kg</span>
            <span class="hint">(物料信息)</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="param-item">
            <span class="label">LeadTime:</span>
            <span class="value readonly">{{ materialInfo.leadtime }} 天</span>
            <span class="hint">(物料信息)</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 15px;">
        <el-col :span="4">
          <div class="param-item">
            <span class="label">安全库存系数:</span>
            <span class="value readonly">{{ materialInfo.safetyFactor }}</span>
            <span class="hint">(物料信息)</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="param-item">
            <span class="label">计算的安全库存:</span>
            <span class="value">{{ predictionSummary.safety_stock?.toFixed(2) || '-' }} kg</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="param-item">
            <span class="label">预测文件:</span>
            <span class="value" v-if="predictionFileExists">
              预测数据_{{ warehouse }}_{{ material }}.csv
              <el-tag size="small" type="success">已存在</el-tag>
            </span>
            <span class="value" v-else style="color: #999;">未生成</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 预测数据Tab -->
      <el-tab-pane label="预测数据" name="prediction">
        <el-card>
          <el-table :data="predictionData" style="width: 100%" max-height="500" stripe>
            <el-table-column prop="日期" label="日期" width="120" fixed />
            <el-table-column prop="预测出货量(kg)" label="预测出货量(kg)" width="150">
              <template #default="{ row }">
                {{ row['预测出货量(kg)']?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="安全库存(kg)" label="安全库存(kg)" width="150">
              <template #default="{ row }">
                {{ row['安全库存(kg)']?.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
          <div class="table-footer">
            <span>共 {{ predictionData.length }} 条数据</span>
            <el-button type="primary" link @click="handleGeneratePrediction">重新生成预测</el-button>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 下单建议Tab -->
      <el-tab-pane label="下单建议" name="order" :disabled="!orderData.length">
        <el-card v-if="orderSummary.order_count">
          <div class="order-summary">
            <el-row :gutter="20">
              <el-col :span="4">
                <div class="summary-item">
                  <div class="summary-value">{{ orderSummary.order_count }}</div>
                  <div class="summary-label">下单次数</div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="summary-item">
                  <div class="summary-value">{{ orderSummary.total_order_qty }}</div>
                  <div class="summary-label">总下单量(kg)</div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="summary-item">
                  <div class="summary-value">{{ orderSummary.min_stock?.toFixed(2) }}</div>
                  <div class="summary-label">最低库存(kg)</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <el-table :data="orderData" style="width: 100%" max-height="400" stripe>
            <el-table-column prop="日期" label="日期" width="120" fixed />
            <el-table-column prop="初始库存(kg)" label="初始库存(kg)" width="120">
              <template #default="{ row }">
                {{ row['初始库存(kg)']?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="预测出货(kg)" label="预测出货(kg)" width="120">
              <template #default="{ row }">
                {{ row['预测出货(kg)']?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="到货量(kg)" label="到货量(kg)" width="100">
              <template #default="{ row }">
                <span :class="{ 'highlight': row['到货量(kg)'] > 0 }">
                  {{ row['到货量(kg)'] || 0 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="结束库存(kg)" label="结束库存(kg)" width="120">
              <template #default="{ row }">
                <span :class="{ 'warning': row['结束库存(kg)'] < row['安全库存(kg)'] }">
                  {{ row['结束库存(kg)']?.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="安全库存(kg)" label="安全库存(kg)" width="120">
              <template #default="{ row }">
                {{ row['安全库存(kg)']?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="是否下单" label="是否下单" width="100">
              <template #default="{ row }">
                <el-tag :type="row['是否下单'] === '是' ? 'danger' : 'info'" size="small">
                  {{ row['是否下单'] }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="下单数量(kg)" label="下单数量(kg)" width="120">
              <template #default="{ row }">
                <span v-if="row['下单数量(kg)']">{{ row['下单数量(kg)'] }} kg</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 图表Tab -->
      <el-tab-pane label="库存图表" name="chart" :disabled="!chartData">
        <el-card>
          <inventory-chart v-if="chartData" :chart-data="chartData" :key="chartKey" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { generatePrediction, readPrediction, generateOrder, readOrder, getChartData, getMaterialInfo } from '../api'
import InventoryChart from '../components/InventoryChart.vue'

const route = useRoute()
const router = useRouter()

const warehouse = computed(() => route.params.warehouse)
const material = computed(() => route.params.material)

const loading = ref(false)
const activeTab = ref('prediction')
const chartKey = ref(0)  // 用于强制刷新图表

const predictionData = ref([])
const predictionSummary = ref({})
const predictionFileExists = ref(false)
const orderData = ref([])
const orderSummary = ref({})
const chartData = ref(null)

// 用户可修改的参数
const initialStock = ref(2000)
const predictDays = ref(60)

// 物料信息（从后端获取，只读）
const materialInfo = ref({
  moq: 0,
  leadtime: 0,
  safetyFactor: 0
})

const loadPrediction = async () => {
  loading.value = true
  try {
    const res = await readPrediction(warehouse.value, material.value)
    if (res.data.success) {
      predictionData.value = res.data.data
      predictionSummary.value = res.data.summary
      predictionFileExists.value = true
    }
  } catch (error) {
    if (error.response?.status !== 404) {
      ElMessage.error('加载预测数据失败')
    }
    predictionFileExists.value = false
  } finally {
    loading.value = false
  }
}

const loadOrder = async () => {
  loading.value = true
  try {
    const res = await readOrder(warehouse.value, material.value)
    if (res.data.success) {
      orderData.value = res.data.data
      orderSummary.value = res.data.summary
    }
  } catch (error) {
    if (error.response?.status !== 404) {
      ElMessage.error('加载下单建议失败')
    }
  } finally {
    loading.value = false
  }
}

const loadChartData = async () => {
  try {
    const res = await getChartData(warehouse.value, material.value, 30)
    if (res.data.success) {
      chartData.value = res.data
      chartKey.value++  // 数据更新时刷新图表
    }
  } catch (error) {
    console.error('加载图表数据失败', error)
  }
}

// 监听Tab切换，切换到图表Tab时刷新图表
watch(activeTab, (newTab) => {
  if (newTab === 'chart' && chartData.value) {
    nextTick(() => {
      chartKey.value++
    })
  }
})

const handleGeneratePrediction = async () => {
  loading.value = true
  try {
    const res = await generatePrediction(
      warehouse.value,
      material.value,
      initialStock.value,
      predictDays.value
    )
    if (res.data.success) {
      ElMessage.success(`预测数据已生成：${res.data.file_name}`)
      // 更新物料信息（从后端返回）
      materialInfo.value = {
        moq: res.data.moq,
        leadtime: res.data.leadtime,
        safetyFactor: res.data.safety_factor
      }
      predictionSummary.value = {
        total_days: res.data.predict_days,
        avg_prediction: res.data.avg_prediction,
        total_prediction: res.data.total_prediction,
        safety_stock: res.data.safety_stock
      }
      predictionFileExists.value = true
      await loadPrediction()
    }
  } catch (error) {
    ElMessage.error('生成预测失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const handleReloadPrediction = async () => {
  await loadPrediction()
  ElMessage.success('预测数据已重新加载')
}

const handleGenerateOrder = async () => {
  loading.value = true
  try {
    const res = await generateOrder(
      warehouse.value,
      material.value,
      initialStock.value,
      materialInfo.value.moq,
      materialInfo.value.leadtime
    )
    if (res.data.success) {
      ElMessage.success(`下单建议已生成：${res.data.file_name}`)
      orderSummary.value = res.data.summary
      await loadOrder()
      await loadChartData()
    }
  } catch (error) {
    ElMessage.error('生成下单建议失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/')
}

const loadMaterialInfo = async () => {
  try {
    const res = await getMaterialInfo(material.value)
    if (res.data.success) {
      materialInfo.value = {
        moq: res.data.moq,
        leadtime: res.data.leadtime,
        safetyFactor: res.data.safety_factor
      }
    }
  } catch (error) {
    console.error('加载物料信息失败', error)
  }
}

onMounted(async () => {
  // 确保参数重置为默认值
  initialStock.value = 2000
  predictDays.value = 60

  // 加载物料信息
  await loadMaterialInfo()

  // 尝试加载已有的预测数据
  await loadPrediction()

  // 如果有预测数据，加载下单建议和图表
  if (predictionFileExists.value) {
    await loadOrder()
    await loadChartData()
  }
})
</script>

<style scoped>
.detail-page {
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  flex: 1;
}

.param-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.param-item .el-input-number {
  width: 150px;
}

.param-item .el-input-number .el-input-number__decrease,
.param-item .el-input-number .el-input-number__increase {
  cursor: pointer;
  pointer-events: auto;
}

.param-item .label {
  color: #666;
  min-width: 100px;
}

.param-item .unit {
  color: #999;
}

.param-item .value {
  font-weight: 500;
}

.param-item .value.readonly {
  color: #409EFF;
  font-weight: bold;
}

.param-item .hint {
  color: #999;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.main-tabs {
  margin-top: 20px;
}

.order-summary {
  padding: 20px 0;
}

.summary-item {
  text-align: center;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.summary-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
}

.highlight {
  color: #67C23A;
  font-weight: bold;
}

.warning {
  color: #F56C6C;
  font-weight: bold;
}
</style>
