import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

/**
 * 根据当前语言返回中文或英文字段
 * 中文 → name / title / description
 * 其他 → name_en / title_en / description_en
 */
export function useDisplay() {
  const { locale } = useI18n()

  const isZh = computed(() => locale.value === 'zh')

  function localField(obj, fieldBase) {
    if (!obj) return ''
    if (isZh.value) return obj[fieldBase] || obj[fieldBase + '_en'] || ''
    return obj[fieldBase + '_en'] || obj[fieldBase] || ''
  }

  function localTitle(obj) { return localField(obj, 'title') }
  function localName(obj) { return localField(obj, 'name') }
  function localDesc(obj) { return localField(obj, 'description') }
  function localPackaging(obj) { return localField(obj, 'packaging_info') }
  function localCustomization(obj) { return localField(obj, 'customization') }

  function localCatName(cat) {
    if (!cat) return ''
    // Support both category objects (name/name_en) and product objects (category_name/category_name_en)
    const zh = cat.name || cat.category_name || ''
    const en = cat.name_en || cat.category_name_en || ''
    if (isZh.value) return zh || en
    return en || zh
  }

  return { isZh, localTitle, localName, localDesc, localPackaging, localCustomization, localCatName }
}
