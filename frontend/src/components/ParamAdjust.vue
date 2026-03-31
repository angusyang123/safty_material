<template>
  <el-card class="param-adjust">
    <template #header>
      <span>参数调整（模拟计算）</span>
    </template>
    <el-form :inline="true" :model="form">
      <el-form-item label="初始库存 (kg)">
        <el-input-number v-model="form.initialStock" :min="0" :step="10" />
      </el-form-item>
      <el-form-item label="安全库存系数">
        <el-input-number
          v-model="form.safetyFactor"
          :min="0.1"
          :max="5"
          :step="0.1"
          :precision="2"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSimulate">模拟计算</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  defaultStock: { type: Number, default: 200 },
  defaultFactor: { type: Number, default: 1.65 }
})

const emit = defineEmits(['simulate'])

const form = ref({
  initialStock: props.defaultStock || 200,
  safetyFactor: props.defaultFactor || 1.65
})

watch([() => props.defaultStock, () => props.defaultFactor], () => {
  form.value.initialStock = props.defaultStock || 200
  form.value.safetyFactor = props.defaultFactor || 1.65
})

const handleSimulate = () => {
  emit('simulate', form.value.initialStock, form.value.safetyFactor)
}
</script>

<style scoped>
.param-adjust {
  margin-bottom: 20px;
}
</style>
