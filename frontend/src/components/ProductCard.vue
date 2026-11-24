<template>
  <div class="product-card glass-card" @click="$router.push(`/products/${product.id}`)" @mouseenter="startCarousel" @mouseleave="stopCarousel">
    <div class="card-image">
      <img :src="currentImage" :alt="localTitle(product)" @error="e => e.target.src = placeholder" />
      <div class="badge-overlay">
        <span v-if="product.is_featured" class="product-badge badge-featured">★ {{ t('product.hotTag') }}</span>
        <span v-if="product.is_new" class="product-badge badge-new">{{ t('product.newTag') }}</span>
        <span v-if="product.is_clearance && clearanceEnabled" class="product-badge badge-clearance">🔥 {{ t('clearance.title') }}</span>
      </div>
      <div v-if="imageCount > 1" class="image-dots">
        <span v-for="(_, i) in product.images" :key="i" class="dot" :class="{ active: i === currentIdx }"></span>
      </div>
    </div>
    <div class="card-info">
      <div class="card-category" v-if="product.category_name">
        {{ localCatName(product) }}
      </div>
      <h3 class="card-title">{{ localTitle(product) }}</h3>
      <div class="card-price-row">
        <div class="price-moq">
          <span class="price" v-if="product.price">${{ product.price }}</span>
          <span class="moq">{{ t('product.moq') }}: {{ product.moq }} {{ t('product.pcs') }}</span>
        </div>
      </div>
      <div v-if="showActions" class="card-actions">
        <el-button type="primary" class="btn-inquire" size="small" @click.stop="$emit('inquire', product)">
          {{ t('product.getQuote') }}
        </el-button>
        <el-button class="btn-wishlist" size="small" @click.stop="addToWishlist">
          🛒 {{ t('wishlist.title') }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useAuth } from '../store/auth'
import { useClearance } from '../composables/useClearance'
import { ElMessage } from 'element-plus'
import api from '../api'

const { t } = useI18n()
const { localTitle, localCatName } = useDisplay()
const { state: authState } = useAuth()
const { clearanceEnabled } = useClearance()
const props = defineProps({ product: Object, hideActions: { type: Boolean, default: false } })
defineEmits(['inquire'])

const showActions = computed(() => {
  if (props.hideActions) return false
  const role = authState.user?.role
  return role === 'buyer'
})

const placeholder = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><rect fill="#e2e8f0" width="400" height="400"/><text fill="#94a3b8" font-size="16" x="50%" y="50%" text-anchor="middle" dy=".3em">No Image</text></svg>'
)
const imageCount = computed(() => props.product.images?.length || 0)
const currentIdx = ref(0)
let carouselTimer = null

const currentImage = computed(() => {
  const imgs = props.product.images
  if (imgs && imgs.length) return imgs[currentIdx.value % imgs.length]
  return placeholder
})

function startCarousel() {
  if (imageCount.value <= 1) return
  carouselTimer = setInterval(() => {
    currentIdx.value = (currentIdx.value + 1) % imageCount.value
  }, 2500)
}

function stopCarousel() {
  if (carouselTimer) { clearInterval(carouselTimer); carouselTimer = null }
  currentIdx.value = 0
}

onUnmounted(() => { if (carouselTimer) clearInterval(carouselTimer) })

async function addToWishlist() {
  try {
    await api.post('/wishlist', { product_id: props.product.id, quantity: 1 })
    ElMessage.success(t('wishlist.title') + ' ✓')
    window.dispatchEvent(new CustomEvent('wishlist-updated'))
  } catch (e) {
    ElMessage.error('Failed to add to wishlist')
  }
}
</script>

<style scoped>
/* --- Industrial Design Card --- */
.product-card {
  background: #fff;
  border: 0.5px solid rgba(15, 23, 42, .05);
  border-radius: 32px;
  padding: 8px;
  cursor: pointer;
  position: relative;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, .02);
  transition: all .7s cubic-bezier(.4, 0, .2, 1);
}
.product-card:hover {
  border-color: rgba(0, 210, 255, .15);
  box-shadow: 0 30px 60px -12px rgba(15, 23, 42, .08);
  transform: translateY(-6px);
}

/* Image area */
.card-image {
  position: relative;
  aspect-ratio: 4 / 5;
  border-radius: 28px;
  overflow: hidden;
  background: #f8fafc;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(0.04);
  transition: transform 1000ms cubic-bezier(.4, 0, .2, 1), filter 1000ms cubic-bezier(.4, 0, .2, 1);
}
.product-card:hover .card-image img {
  transform: scale(1.1);
  filter: grayscale(0);
}

/* Badge overlay */
.badge-overlay {
  position: absolute;
  top: 14px;
  left: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 3;
}
.product-badge {
  display: inline-block;
  padding: 5px 12px;
  font-size: 9px;
  font-weight: 900;
  font-family: 'Space Grotesk', sans-serif;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border-radius: 10px;
  white-space: nowrap;
  line-height: 1.4;
  color: #fff;
  border: none;
}
.badge-featured {
  background: #f59e0b;
}
.badge-new {
  background: #16a34a;
}
.badge-clearance {
  background: #dc2626;
}

/* Image carousel dots */
.image-dots {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 5px;
  z-index: 3;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255,255,255,.5);
  transition: all .3s ease;
}
.dot.active {
  background: #fff;
  width: 16px;
  border-radius: 3px;
}

/* Info area */
.card-info {
  padding: 20px 24px 24px;
}
.card-category {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 900;
  font-family: 'Space Grotesk', sans-serif;
  color: #94a3b8;
  margin-bottom: 8px;
}
.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  font-family: 'Manrope', sans-serif;
  line-height: 1.35;
  color: #0F172A;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0 0 14px;
  min-height: 2.7rem;
  transition: color .7s cubic-bezier(.4, 0, .2, 1);
}
.product-card:hover .card-title {
  color: #1d4ed8;
}

/* Price / MOQ row */
.card-price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.price-moq {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.price {
  color: #7000ff;
  font-weight: 900;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.125rem;
  line-height: 1.2;
}
.moq {
  font-size: 9px;
  text-transform: uppercase;
  font-weight: 900;
  font-family: 'Space Grotesk', sans-serif;
  color: #64748b;
  letter-spacing: 0.12em;
}
/* Add button */
.add-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 0.5px solid rgba(15, 23, 42, .05);
  background: #fff;
  color: #0F172A;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all .7s cubic-bezier(.4, 0, .2, 1);
}
.add-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
  color: #fff;
  box-shadow: 0 10px 25px -5px rgba(0, 210, 255, .2);
}

/* Buyer card-actions */
.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.btn-inquire {
  flex: 1;
  font-weight: 700;
  font-family: 'Manrope', sans-serif;
  border-radius: 16px;
}
.btn-wishlist {
  flex: 1;
  background: #fff;
  border: 0.5px solid rgba(15, 23, 42, .05);
  color: #64748b;
  border-radius: 16px;
  transition: all .7s cubic-bezier(.4, 0, .2, 1);
}
.btn-wishlist:hover {
  background: rgba(29, 78, 216, .06);
  border-color: rgba(29, 78, 216, .2);
  color: #1d4ed8;
}
</style>
