<template>
  <div ref="chartRef" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Object, default: () => ({ data: [], metrics: {} }) }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return

  const validData = (props.data.data || []).filter(d => d.predicted !== null)
  if (!validData.length) return

  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)

  const dates = validData.map(d => d.date)
  const actuals = validData.map(d => d.actual)
  const predicteds = validData.map(d => d.predicted)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['实际出货', '预测出货'] },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, interval: Math.floor(dates.length / 10) }
    },
    yAxis: { type: 'value', name: '出货量 (kg)' },
    series: [
      {
        name: '实际出货',
        type: 'line',
        data: actuals,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '预测出货',
        type: 'line',
        data: predicteds,
        itemStyle: { color: '#E6A23C' },
        lineStyle: { type: 'dashed' }
      }
    ]
  }

  chart.setOption(option)
}

watch(() => props.data, initChart, { deep: true })
onMounted(initChart)
</script>
