<!-- views/management/MemberFormView.vue -->
<template>
  <MemberForm :id="id" :mode="mode" />
</template>

<script setup>
  import MemberForm from '@/components/team/MemberForm.vue'

  // 接收路由傳遞的 props
  const props = defineProps({
    mode: {
      type: String,
      required: true,
      validator: value => ['add', 'edit'].includes(value)
    },
    id: {
      type: [String, Number],
      default: null
    }
  })

  // 可以在這裡加入頁面級別的邏輯，比如：
  // - 頁面標題設定
  // - 權限檢查
  // - 分析追蹤等

  // 設置頁面標題
  import { computed } from 'vue' // 如果你使用 @vueuse/head

  const pageTitle = computed(() => {
    return props.mode === 'add' ? '新增球隊成員' : '編輯成員資料'
  })
</script>

<!-- 無需額外樣式，因為 MemberForm 組件已經包含了所有樣式 -->
