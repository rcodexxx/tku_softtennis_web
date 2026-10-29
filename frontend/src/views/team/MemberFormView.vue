<template>
  <MemberForm :mode="mode" :member-id="id ? Number(id) : null" />
</template>

<script setup>
  import MemberForm from '@/components/team/MemberForm.vue'

  defineProps({
    mode: { type: String, required: true, validator: value => ['add', 'edit'].includes(value) },
    id: { type: [String, Number], default: null }
  })
</script>
