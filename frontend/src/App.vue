<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import gsap from 'gsap'
import ChatView from './views/ChatView.vue'

const blobRefs = useTemplateRef<HTMLSpanElement[]>('blobs')

onMounted(() => {
  gsap.to(blobRefs.value, {
    x: () => gsap.utils.random(-60, 60),
    y: () => gsap.utils.random(-40, 40),
    duration: () => gsap.utils.random(10, 16),
    repeat: -1,
    yoyo: true,
    ease: 'sine.inOut',
    stagger: 1.5,
  })
})
</script>

<template>
  <div class="bg-blobs" aria-hidden="true">
    <span v-for="n in 3" ref="blobs" :key="n"></span>
  </div>
  <ChatView />
</template>
