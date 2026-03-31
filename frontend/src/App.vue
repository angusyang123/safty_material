<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>库存预测分析系统</h1>
        <el-button type="primary" @click="reloadData" :loading="loading">
          重新加载数据
        </el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { reloadMaterials } from './api'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const reloadData = async () => {
  loading.value = true
  try {
    await reloadMaterials()
    ElMessage.success('数据重新加载成功')
    window.location.reload()
  } catch (error) {
    ElMessage.error('数据加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  min-height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.el-header h1 {
  margin: 0;
  font-size: 20px;
}
</style>
