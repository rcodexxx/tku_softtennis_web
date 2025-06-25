<template>
  <div class="match-record-form-view">
    <!-- 權限錯誤提示 -->
    <n-alert
      v-if="showPermissionError"
      type="warning"
      title="權限不足"
      closable
      style="margin-bottom: 1rem;"
      @close="showPermissionError = false"
    >
      您沒有足夠的權限進行此操作。編輯和刪除比賽記錄需要幹部以上權限。
    </n-alert>

    <!-- 主要表單組件 -->
    <MatchRecordForm
      :mode="mode"
      :match-id="matchId"
      @permission-error="handlePermissionError"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NAlert } from 'naive-ui'

// 引入統一的比賽記錄表單組件
import MatchRecordForm from '@/components/match/MatchRecordForm.vue'

// 定義 Props (從路由傳入)
defineProps({
  mode: {
    type: String,
    required: true,
    validator: value => ['add', 'edit', 'view'].includes(value)
  },
  matchId: {
    type: [String, Number],
    default: null
  }
})
// 響應式數據
const route = useRoute()
const showPermissionError = ref(false)

// 檢查路由查詢參數中的錯誤
onMounted(() => {
  if (route.query.error === 'insufficient_permissions') {
    showPermissionError.value = true
  }
})

// 處理權限錯誤
const handlePermissionError = () => {
  showPermissionError.value = true
}
</script>

<style scoped>
.match-record-form-view {
  min-height: 100vh;
  background: #f5f5f5;
}
</style>