<template>
  <div class="overview-table">
    <el-table :data="data" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="warehouse" label="仓库" width="120" />
      <el-table-column prop="material" label="物料" width="120" />
      <el-table-column prop="current_stock" label="当前库存(kg)" width="130">
        <template #default="{ row }">
          {{ row.current_stock?.toFixed(1) }}
        </template>
      </el-table-column>
      <el-table-column prop="safety_stock" label="安全库存(kg)" width="130">
        <template #default="{ row }">
          {{ row.safety_stock?.toFixed(1) }}
        </template>
      </el-table-column>
      <el-table-column label="下单建议" width="180">
        <template #default="{ row }">
          <el-tag v-if="row.need_order" type="danger">
            建议 {{ row.order_date }} 下单
          </el-tag>
          <el-tag v-else type="success">暂无需下单</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="order_quantity" label="下单数量(kg)" width="120">
        <template #default="{ row }">
          {{ row.order_quantity || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="leadtime" label="Lead Time(天)" width="130" />
      <el-table-column prop="moq" label="MOQ(kg)" width="100" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="$emit('view-detail', row.warehouse, row.material)"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view-detail'])
</script>

<style scoped>
.overview-table {
  background: white;
  padding: 20px;
  border-radius: 4px;
}
</style>
