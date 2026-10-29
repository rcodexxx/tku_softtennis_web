<template>
  <div class="avatar-uploader" :style="{ '--size': `${size}px` }">
    <button type="button" class="avatar-button" :disabled="uploading" title="更換頭像" @click="input?.click()">
      <PlayerAvatar :id="memberId" :name="name" :src="src" :size="size" />
      <span class="overlay">
        <n-spin v-if="uploading" size="small" stroke="#fff" />
        <n-icon v-else :component="CameraOutline" size="22" />
      </span>
    </button>
    <button v-if="src && !uploading" type="button" class="remove" title="移除頭像" @click="remove">
      <n-icon :component="CloseOutline" size="14" />
    </button>
    <input ref="input" type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden @change="upload" />
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { useDialog, useMessage } from 'naive-ui'
  import { CameraOutline, CloseOutline } from '@vicons/ionicons5'
  import { membersApi } from '@/api'
  import PlayerAvatar from './PlayerAvatar.vue'

  const MAX_BYTES = 3 * 1024 * 1024

  /** 點擊頭像上傳照片；上傳或移除後以 updated 回傳最新的球員資料。 */
  const props = defineProps({
    memberId: { type: Number, required: true },
    name: { type: String, default: '' },
    src: { type: String, default: null },
    size: { type: Number, default: 96 }
  })

  const emit = defineEmits(['updated'])

  const message = useMessage()
  const dialog = useDialog()
  const input = ref(null)
  const uploading = ref(false)

  const upload = async event => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    if (file.size > MAX_BYTES) {
      message.error('圖片不能超過 3MB')
      return
    }
    uploading.value = true
    try {
      emit('updated', await membersApi.uploadAvatar(props.memberId, file))
      message.success('頭像已更新')
    } catch (error) {
      message.error(error.response?.data?.message || '上傳失敗')
    } finally {
      uploading.value = false
    }
  }

  const remove = () => {
    dialog.warning({
      title: '移除頭像',
      content: '確定要移除目前的頭像嗎？',
      positiveText: '移除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          emit('updated', await membersApi.removeAvatar(props.memberId))
        } catch (error) {
          message.error(error.response?.data?.message || '移除失敗')
        }
      }
    })
  }
</script>

<style scoped>
  .avatar-uploader {
    position: relative;
    width: var(--size);
    height: var(--size);
  }
  .avatar-button {
    position: relative;
    padding: 0;
    border: none;
    border-radius: 50%;
    background: none;
    cursor: pointer;
  }
  .overlay {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    background: rgba(7, 20, 51, 0.5);
    opacity: 0;
    transition: opacity var(--duration-fast);
  }
  .avatar-button:hover .overlay,
  .avatar-button:focus-visible .overlay,
  .avatar-button:disabled .overlay {
    opacity: 1;
  }
  .remove {
    position: absolute;
    top: 2px;
    right: 2px;
    width: 24px;
    height: 24px;
    border: 2px solid #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--red-500);
    color: #fff;
    cursor: pointer;
  }
</style>
