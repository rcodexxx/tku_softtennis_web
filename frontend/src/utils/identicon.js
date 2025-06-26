// frontend/src/services/identiconUtils.js

class IdenticonGenerator {
  constructor() {
    this.jdenticonLoaded = false
    this.loadingPromise = null
  }

  /**
   * 載入 jdenticon 庫
   * @returns {Promise<boolean>} 載入成功返回 true
   */
  async loadJdenticon() {
    if (this.jdenticonLoaded || window.jdenticon) {
      this.jdenticonLoaded = true
      return true
    }

    // 如果正在載入中，返回現有的 Promise
    if (this.loadingPromise) {
      return this.loadingPromise
    }

    this.loadingPromise = new Promise((resolve, reject) => {
      try {
        const script = document.createElement('script')
        script.src = 'https://cdn.jsdelivr.net/npm/jdenticon@3.2.0/dist/jdenticon.min.js'
        script.async = true

        script.onload = () => {
          this.jdenticonLoaded = true
          console.log('✅ jdenticon 載入成功')
          resolve(true)
        }

        script.onerror = () => {
          console.error('❌ jdenticon 載入失敗')
          reject(false)
        }

        document.head.appendChild(script)
      } catch (error) {
        console.error('載入 jdenticon 時發生錯誤:', error)
        reject(false)
      }
    })

    return this.loadingPromise
  }

  /**
   * 生成 identicon
   * @param {HTMLElement} svgElement - SVG 元素
   * @param {string} text - 用於生成 identicon 的文字
   * @param {object} options - 選項
   * @param {number} options.size - 大小 (可選)
   * @param {boolean} options.useJdenticon - 是否優先使用 jdenticon (預設 true)
   */
  async generateIdenticon(svgElement, text, options = {}) {
    const { size, useJdenticon = true } = options

    if (!svgElement || !text) {
      console.warn('SVG元素或文字不存在，跳過identicon生成')
      return
    }

    console.log('開始生成identicon for:', text)

    if (useJdenticon) {
      // 如果 jdenticon 還沒載入，先載入它
      if (!this.jdenticonLoaded || !window.jdenticon) {
        try {
          await this.loadJdenticon()
          this.generateWithJdenticon(svgElement, text, size)
        } catch (error) {
          // 如果載入失敗，使用 fallback
          this.generateFallbackIdenticon(svgElement, text, size)
        }
      } else {
        this.generateWithJdenticon(svgElement, text, size)
      }
    } else {
      this.generateFallbackIdenticon(svgElement, text, size)
    }
  }

  /**
   * 使用 jdenticon 生成
   * @param {HTMLElement} svgElement - SVG 元素
   * @param {string} text - 文字
   * @param {number} size - 大小
   */
  generateWithJdenticon(svgElement, text, size) {
    try {
      if (!window.jdenticon || !svgElement) {
        throw new Error('jdenticon 不可用')
      }

      // 使用 jdenticon 生成
      svgElement.setAttribute('data-jdenticon-value', text)
      window.jdenticon.updateSvg(svgElement, text)

      console.log('✅ jdenticon Identicon生成完成')
    } catch (error) {
      console.error('❌ jdenticon 生成失敗:', error)
      this.generateFallbackIdenticon(svgElement, text, size)
    }
  }

  /**
   * 生成 fallback identicon
   * @param {HTMLElement} svgElement - SVG 元素
   * @param {string} text - 文字
   * @param {number} size - 大小
   */
  generateFallbackIdenticon(svgElement, text, size) {
    try {
      if (!svgElement) return

      // 簡單的 fallback - 生成基於文字的顏色圓形
      let hash = 0
      for (let i = 0; i < text.length; i++) {
        const char = text.charCodeAt(i)
        hash = (hash << 5) - hash + char
        hash = hash & hash
      }

      const hue = Math.abs(hash) % 360
      const saturation = 50 + (Math.abs(hash) % 30)
      const lightness = 45 + (Math.abs(hash) % 20)
      const bgColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`

      const svgSize = size || svgElement.getAttribute('width') || 24
      const centerX = svgSize / 2
      const centerY = svgSize / 2
      const radius = svgSize / 2

      // 生成簡單的 SVG
      svgElement.innerHTML = `
        <circle cx="${centerX}" cy="${centerY}" r="${radius}" fill="${bgColor}"/>
        <text x="${centerX}" y="${centerY + 6}" text-anchor="middle" fill="white" font-size="${svgSize * 0.4}" font-weight="bold">
          ${text.charAt(0).toUpperCase()}
        </text>
      `

      console.log('✅ Fallback identicon 生成完成')
    } catch (error) {
      console.error('❌ Fallback identicon 生成失敗:', error)
    }
  }

  /**
   * 批量生成 identicon
   * @param {Array} items - 要生成的項目列表
   * @param {Function} getSvgElement - 獲取 SVG 元素的函數
   * @param {Function} getText - 獲取文字的函數
   * @param {object} options - 選項
   */
  async generateBatchIdenticons(items, getSvgElement, getText, options = {}) {
    for (const item of items) {
      const svgElement = getSvgElement(item)
      const text = getText(item)
      if (svgElement && text) {
        await this.generateIdenticon(svgElement, text, options)
      }
    }
  }
}

// 創建單例實例
const identiconGenerator = new IdenticonGenerator()

/**
 * 便捷函數：生成單個 identicon
 * @param {HTMLElement} svgElement - SVG 元素
 * @param {string} text - 文字
 * @param {object} options - 選項
 */
export const generateIdenticon = async (svgElement, text, options = {}) => {
  return identiconGenerator.generateIdenticon(svgElement, text, options)
}

/**
 * 便捷函數：生成多個 identicon
 * @param {Array} items - 項目列表
 * @param {Function} getSvgElement - 獲取 SVG 元素的函數
 * @param {Function} getText - 獲取文字的函數
 * @param {object} options - 選項
 */
export const generateBatchIdenticons = async (items, getSvgElement, getText, options = {}) => {
  return identiconGenerator.generateBatchIdenticons(items, getSvgElement, getText, options)
}

/**
 * 便捷函數：預載入 jdenticon 庫
 */
export const preloadJdenticon = async () => {
  return identiconGenerator.loadJdenticon()
}

/**
 * 便捷函數：根據用戶數據生成文字
 * @param {object} user - 用戶對象
 * @param {boolean} useRealName - 是否優先使用真實姓名
 * @returns {string} 用於生成 identicon 的文字
 */
export const getUserIdenticonText = (user, useRealName = true) => {
  if (!user) return 'User'

  if (useRealName) {
    // 優先使用真實姓名
    return user.member_profile?.name ||
           user.display_name ||
           user.username ||
           'User'
  } else {
    // 優先使用暱稱
    return user.display_name ||
           user.member_profile?.name ||
           user.username ||
           'User'
  }
}

/**
 * 便捷函數：為用戶頭像生成 identicon
 * @param {HTMLElement} svgElement - SVG 元素
 * @param {object} user - 用戶對象
 * @param {object} options - 選項
 * @param {boolean} options.useRealName - 是否優先使用真實姓名 (預設 true)
 */
export const generateUserIdenticon = async (svgElement, user, options = {}) => {
  const { useRealName = true, ...otherOptions } = options
  const text = getUserIdenticonText(user, useRealName)
  return generateIdenticon(svgElement, text, otherOptions)
}

// 匯出類別供進階使用
export { IdenticonGenerator }

// 預設匯出單例實例
export default identiconGenerator