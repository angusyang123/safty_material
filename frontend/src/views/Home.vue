<template>
  <div class="home">
    <overview-table
      :data="overviewData"
      :loading="loading"
      @view-detail="goToDetail"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import OverviewTable from '../components/OverviewTable.vue'
import { getOverview } from '../api'

const router = useRouter()
const overviewData = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const response = await getOverview()
    overviewData.value = response.data
  } catch (error) {
    console.error('获取总览数据失败:', error)
  } finally {
    loading.value = false
  }
}

const goToDetail = (warehouse, material) => {
  router.push(`/detail/${warehouse}/${material}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home {
  padding: 20px;
}
</style>
