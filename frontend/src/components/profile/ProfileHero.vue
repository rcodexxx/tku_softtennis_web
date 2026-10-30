<template>
  <section class="hero">
    <div class="hero-bg" aria-hidden="true"></div>
    <AvatarUploader
      v-if="member"
      :member-id="member.id"
      :name="member.name"
      :src="member.avatar_url"
      :size="104"
      class="hero-avatar"
      @updated="value => emit('avatar-updated', value)"
    />
    <PlayerAvatar v-else :name="profile.display_name || profile.username" :size="104" class="hero-avatar" />

    <div class="hero-text">
      <p class="greeting">{{ greeting }}，</p>
      <h1 class="name">{{ profile.display_name || member?.name || profile.username }}</h1>
      <div class="tags">
        <span class="tag role">{{ roleLabel }}</span>
        <span v-if="member?.organization" class="tag">{{
          member.organization.short_name || member.organization.name
        }}</span>
      </div>
    </div>

    <div class="hero-actions">
      <n-button secondary strong class="hero-button" @click="emit('edit')">
        <template #icon><n-icon :component="Edit" /></template>
        編輯資料
      </n-button>
      <n-button secondary strong class="hero-button" @click="emit('change-password')">
        <template #icon><n-icon :component="Password" /></template>
        修改密碼
      </n-button>
    </div>
  </section>
</template>

<script setup>
  import { computed } from 'vue'
  import { Edit, Password } from '@vicons/carbon'
  import AvatarUploader from '@/components/base/AvatarUploader.vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { useOptions } from '@/composables/useOptions'

  const props = defineProps({ profile: { type: Object, required: true } })
  const emit = defineEmits(['edit', 'change-password', 'avatar-updated'])

  const { getRoleDisplay } = useOptions()
  const member = computed(() => props.profile.member)
  const roleLabel = computed(() => getRoleDisplay(props.profile.role))
  const greeting = computed(() => {
    const hour = new Date().getHours()
    return hour < 11 ? '早安' : hour < 18 ? '午安' : '晚安'
  })
</script>

<style scoped>
  .hero {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 28px 32px;
    border-radius: var(--radius-xl);
    background: var(--ink);
    color: var(--bg);
    box-shadow: var(--shadow-lg);
    margin-bottom: 24px;
  }
  .hero-bg {
    position: absolute;
    right: -60px;
    top: -80px;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    border: 40px solid color-mix(in srgb, var(--bg) 6%, transparent);
  }
  .hero-avatar {
    position: relative;
  }
  .hero-text {
    position: relative;
    flex: 1;
    min-width: 0;
  }
  .greeting {
    margin: 0;
    color: var(--blue-200);
    font-weight: 600;
  }
  .name {
    margin: 2px 0 10px;
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 0.02em;
  }
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .tag {
    padding: 3px 12px;
    border-radius: var(--radius-full);
    background: color-mix(in srgb, var(--bg) 14%, transparent);
    font-size: 15px;
    font-weight: 600;
  }
  .tag.role {
    background: var(--red-500);
  }
  .hero-actions {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .hero-button {
    --n-color: color-mix(in srgb, var(--bg) 14%, transparent) !important;
    --n-color-hover: color-mix(in srgb, var(--bg) 22%, transparent) !important;
    --n-color-pressed: color-mix(in srgb, var(--bg) 28%, transparent) !important;
    --n-text-color: var(--bg) !important;
    --n-text-color-hover: var(--bg) !important;
    --n-text-color-pressed: var(--bg) !important;
  }

  @media (max-width: 720px) {
    .hero {
      flex-direction: column;
      text-align: center;
      padding: 24px 18px;
    }
    .tags {
      justify-content: center;
    }
    .hero-actions {
      flex-direction: row;
    }
  }
</style>
