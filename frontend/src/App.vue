<template>
  <div id="app-root">
    <AppHeader />
    <main style="min-height: calc(100vh - 160px)">
      <router-view />
    </main>
    <AppFooter />
    <FloatingWidgets :wishlist-count="wishlistCount" @toggle-wishlist="toggleWishlist" />
    <WishList ref="wishlistRef" @update:count="n => wishlistCount = n" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import FloatingWidgets from './components/FloatingWidgets.vue'
import WishList from './components/WishList.vue'

const wishlistRef = ref(null)
const wishlistCount = ref(0)

function toggleWishlist() {
  wishlistRef.value?.toggle()
}
</script>
