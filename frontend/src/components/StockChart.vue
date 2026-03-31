<template>
  <div ref="chartRef" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  predictions: { type: Array, default: () => [] },
  stocks: { type: Array, default: () => [] },
  safetyStock: { type: Number, default: 0 },
  leadtime: { type: Number, default: 0 }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value || !props.predictions.length) return

  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)

  const days = props.predictions.map((_, i) => `第${i + 1}天`)
  const safetyLine = Array(props.predictions.length).fill(props.safetyStock)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['预测出货量', '预测库存', '安全库存线'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', name: '数量 (kg)' },
    series: [
      {
        name: '预测出货量',
        type: 'bar',
        data: props.predictions,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '预测库存',
        type: 'line',
        data: props.stocks,
        itemStyle: { color: '#67C23A' },
        lineStyle: { width: 3 }
      },
      {
        name: '安全库存线',
        type: 'line',
        data: safetyLine,
        itemStyle: { color: '#F56C6C' },
        lineStyle: { type: 'dashed', width: 2 },
        symbol: 'none'
      }
    ]
  }

  chart.setOption(option)
}

watch(() => [props.predictions, props.stocks, props.safetyStock], initChart, { deep: true })
onMounted(initChart)
</script>
