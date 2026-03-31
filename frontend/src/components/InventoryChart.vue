<template>
  <div class="inventory-chart" ref="chartContainer">
    <div v-if="!chartData" class="no-data">
      请先生成预测数据和下单建议
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  chartData: {
    type: Object,
    default: null
  }
})

const chartContainer = ref(null)
let chartInstance = null
let resizeObserver = null
let lastWidth = 0
let lastHeight = 0

const initChart = () => {
  if (!chartContainer.value || !props.chartData) return

  const container = chartContainer.value
  const width = container.clientWidth
  const height = container.clientHeight

  // 如果容器尺寸为0，不初始化
  if (width === 0 || height === 0) return

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }

  chartInstance = echarts.init(container)
  lastWidth = width
  lastHeight = height

  const { history, predict } = props.chartData

  // 合并日期
  const allDates = [...(history?.dates || []), ...(predict?.dates || [])]

  // 历史出货量（前30天）
  const historyOutbound = history?.outbound || []
  // 预测出货量
  const predictOutbound = predict?.outbound || []
  // 预测进货量
  const predictInbound = predict?.inbound || []
  // 预测库存
  const predictStock = predict?.stock || []
  // 安全库存
  const safetyStock = predict?.safety_stock || 0

  const option = {
    title: {
      text: '库存预测分析图',
      left: 'center'
    },
    dataZoom: [
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 20,
        bottom: 50
      },
      {
        type: 'inside',
        start: 0,
        end: 100
      }
    ],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        if (!params || !params.length) return ''
        const dataIndex = params[0].dataIndex
        const date = allDates[dataIndex]
        let result = `${date}<br/>`

        params.forEach(param => {
          if (param.value !== undefined) {
            const seriesName = param.seriesName
            const value = Array.isArray(param.data) ? param.data[1] : param.data
            if (value !== null && value !== undefined) {
              result += `${param.marker} ${seriesName}: ${value.toFixed(2)} kg<br/>`
            }
          }
        })
        return result
      }
    },
    legend: {
      data: ['历史出货量', '预测出货量', '预测进货量', '预测库存', '安全库存线'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '22%',
      top: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: allDates,
      axisLabel: {
        rotate: 45,
        interval: Math.max(Math.floor(allDates.length / 10), 0),
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      name: '数量 (kg)',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '历史出货量',
        type: 'bar',
        data: historyOutbound,
        itemStyle: { color: '#409EFF' },
        barMaxWidth: 20
      },
      {
        name: '预测出货量',
        type: 'bar',
        data: [...new Array(historyOutbound.length).fill(null), ...predictOutbound],
        itemStyle: { color: '#E6A23C' },
        barMaxWidth: 20
      },
      {
        name: '预测进货量',
        type: 'bar',
        data: [...new Array(historyOutbound.length).fill(null), ...predictInbound],
        itemStyle: { color: '#F56C6C' },
        barMaxWidth: 20
      },
      {
        name: '预测库存',
        type: 'line',
        data: [...new Array(historyOutbound.length).fill(null), ...predictStock],
        itemStyle: { color: '#67C23A' },
        lineStyle: { width: 2 },
        symbol: 'circle',
        symbolSize: 4
      },
      {
        name: '安全库存线',
        type: 'line',
        data: new Array(allDates.length).fill(safetyStock),
        itemStyle: { color: '#F56C6C' },
        lineStyle: { type: 'dashed', width: 2 },
        symbol: 'none'
      }
    ]
  }

  chartInstance.setOption(option)
}

const handleResize = () => {
  if (!chartInstance || !chartContainer.value) return

  const width = chartContainer.value.clientWidth
  const height = chartContainer.value.clientHeight

  // 只有尺寸真正变化时才resize
  if (width !== lastWidth || height !== lastHeight) {
    lastWidth = width
    lastHeight = height
    if (width > 0 && height > 0) {
      chartInstance.resize()
    }
  }
}

const tryInitChart = () => {
  nextTick(() => {
    if (!chartContainer.value) return

    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight

    if (width > 0 && height > 0) {
      initChart()
    }
  })
}

onMounted(() => {
  // 使用 ResizeObserver 监听容器尺寸变化
  resizeObserver = new ResizeObserver(() => {
    if (!chartContainer.value) return

    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight

    if (width > 0 && height > 0) {
      if (!chartInstance) {
        initChart()
      } else {
        handleResize()
      }
    }
  })

  if (chartContainer.value) {
    resizeObserver.observe(chartContainer.value)
  }

  window.addEventListener('resize', handleResize)

  // 初始尝试初始化
  tryInitChart()
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

watch(() => props.chartData, () => {
  nextTick(() => {
    // 数据变化时重新初始化图表
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
    tryInitChart()
  })
}, { deep: true })
</script>

<style scoped>
.inventory-chart {
  width: 100%;
  height: 550px;
  min-height: 550px;
}

.no-data {
  width: 100%;
  height: 550px;
  min-height: 550px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
