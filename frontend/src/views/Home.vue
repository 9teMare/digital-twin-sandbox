<template>
  <div class="home-container">
    <!-- 背景层：网格 + 辉光 -->
    <div class="bg-fx" aria-hidden="true">
      <div class="bg-grid"></div>
      <div class="bg-glow glow-violet"></div>
      <div class="bg-glow glow-orange"></div>
    </div>

    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-brand">
        <AppLogo size="md" />
        <span class="brand-text">DIGITAL TWIN AGENT SANDBOX</span>
      </div>
      <div class="nav-links">
        <div class="header-controls">
          <ThemeSwitcher />
          <LanguageSwitcher />
        </div>
        <router-link to="/characters" class="nav-link-btn">{{ $t('characters.navLink') }}</router-link>
        <router-link to="/user-agent-creation" class="nav-link-btn">{{ $t('home.userAgentCreationNav') }}</router-link>
        <a href="https://github.com/9teMare/digital-twin-sandbox" target="_blank" class="github-link">
          {{ $t('nav.visitGithub') }} <span class="arrow">↗</span>
        </a>
      </div>
    </nav>

    <div class="main-content">
      <!-- 上半部分：Hero 区域 -->
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">{{ $t('home.tagline') }}</span>
            <span class="version-text">{{ $t('home.version') }}</span>
          </div>

          <h1 class="main-title">
            {{ $t('home.heroTitle1') }}<br>
            <span class="gradient-text">{{ $t('home.heroTitle2') }}</span>
          </h1>

          <div class="hero-desc">
            <p>
              <i18n-t keypath="home.heroDesc" tag="span">
                <template #brand><span class="highlight-bold">{{ $t('home.heroDescBrand') }}</span></template>
                <template #agentScale><span class="highlight-orange">{{ $t('home.heroDescAgentScale') }}</span></template>
                <template #optimalSolution><span class="highlight-code">{{ $t('home.heroDescOptimalSolution') }}</span></template>
              </i18n-t>
            </p>
            <p class="slogan-text">
              {{ $t('home.slogan') }}<span class="blinking-cursor">_</span>
            </p>
          </div>

          <div class="decoration-square"></div>
        </div>

        <div class="hero-right">
          <!-- Cubes 三维交互网格 -->
          <div class="cubes-viewport">
            <div class="corner tl"></div>
            <div class="corner tr"></div>
            <div class="corner bl"></div>
            <div class="corner br"></div>
            <span class="viewport-label">NEURAL.LATTICE // INTERACTIVE</span>
            <div class="cubes-holder">
              <Cubes
                :grid-size="8"
                :max-angle="60"
                :radius="4"
                :border-style="cubeBorder"
                :face-color="cubeFace"
                ripple-color="#ff5a2c"
                :ripple-speed="1.6"
                :auto-animate="true"
                :ripple-on-click="true"
              />
            </div>
          </div>

          <button class="scroll-down-btn" @click="scrollToBottom">
            ↓
          </button>
        </div>
      </section>

      <!-- 下半部分：双栏布局 -->
      <section class="dashboard-section">
        <!-- 左栏：状态与步骤 -->
        <div class="left-panel">
          <div class="panel-header">
            <span class="status-dot">■</span> {{ $t('home.systemStatus') }}
          </div>

          <h2 class="section-title">{{ $t('home.systemReady') }}</h2>
          <p class="section-desc">
            {{ $t('home.systemReadyDesc') }}
          </p>

          <!-- 数据指标卡片 -->
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-value">{{ $t('home.metricLowCost') }}</div>
              <div class="metric-label">{{ $t('home.metricLowCostDesc') }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ $t('home.metricHighAvail') }}</div>
              <div class="metric-label">{{ $t('home.metricHighAvailDesc') }}</div>
            </div>
          </div>

          <!-- 项目模拟步骤介绍 -->
          <div class="steps-container">
            <div class="steps-header">
               <span class="diamond-icon">◇</span> {{ $t('home.workflowSequence') }}
            </div>
            <div class="workflow-list">
              <div class="workflow-item">
                <span class="step-num">01</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step01Title') }}</div>
                  <div class="step-desc">{{ $t('home.step01Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">02</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step02Title') }}</div>
                  <div class="step-desc">{{ $t('home.step02Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">03</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step03Title') }}</div>
                  <div class="step-desc">{{ $t('home.step03Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">04</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step04Title') }}</div>
                  <div class="step-desc">{{ $t('home.step04Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">05</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step05Title') }}</div>
                  <div class="step-desc">{{ $t('home.step05Desc') }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右栏：交互控制台 -->
        <div class="right-panel">
          <div class="console-box">
            <!-- 上传区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ $t('home.realitySeed') }}</span>
                <span class="console-meta">{{ $t('home.supportedFormats') }}</span>
              </div>

              <div
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt"
                  @change="handleFileSelect"
                  style="display: none"
                  :disabled="loading"
                />

                <div v-if="files.length === 0" class="upload-placeholder">
                  <div class="upload-icon">↑</div>
                  <div class="upload-title">{{ $t('home.dragToUpload') }}</div>
                  <div class="upload-hint">{{ $t('home.orBrowse') }}</div>
                </div>

                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="console-divider">
              <span>{{ $t('home.inputParams') }}</span>
            </div>

            <!-- 输入区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ $t('home.simulationPrompt') }}</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  :placeholder="$t('home.promptPlaceholder')"
                  rows="6"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">{{ $t('home.engineBadge') }}</div>
              </div>
            </div>

            <!-- 启动按钮 -->
            <div class="console-section btn-section">
              <button
                class="start-engine-btn"
                @click="startSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">{{ $t('home.startEngine') }}</span>
                <span v-else>{{ $t('home.initializing') }}</span>
                <span class="btn-arrow">→</span>
              </button>
              <router-link to="/user-agent-creation" class="user-agent-btn">
                <span>{{ $t('home.userAgentCreationBtn') }}</span>
                <span class="btn-arrow">→</span>
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- 历史项目数据库 -->
      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import AppLogo from '../components/AppLogo.vue'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'
import Cubes from '../components/Cubes.vue'
import { useTheme } from '../store/theme.js'

const router = useRouter()

// Cubes 颜色随主题切换（gsap 需要具体色值，无法直接用 CSS 变量）
const { resolvedTheme } = useTheme()
const cubeFace = computed(() => (resolvedTheme.value === 'dark' ? '#0b0c16' : '#e6e7f0'))
const cubeBorder = computed(() =>
  resolvedTheme.value === 'dark' ? '1px solid rgba(109, 91, 255, 0.35)' : '1px solid rgba(109, 91, 255, 0.45)'
)

// 表单数据
const formData = ref({
  simulationRequirement: ''
})

// 文件列表
const files = ref([])

// 状态
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)

// 文件输入引用
const fileInput = ref(null)

// 计算属性:是否可以提交
const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

// 触发文件选择
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

// 处理拖拽相关
const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return

  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

// 添加文件
const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

// 移除文件
const removeFile = (index) => {
  files.value.splice(index, 1)
}

// 滚动到底部
const scrollToBottom = () => {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth'
  })
}

// 开始模拟 - 立即跳转，API调用在Process页面进行
const startSimulation = () => {
  if (!canSubmit.value || loading.value) return

  // 存储待上传的数据
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)

    // 立即跳转到Process页面（使用特殊标识表示新建项目）
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}
</script>

<style scoped>
/* 全局变量与重置 */
.home-container {
  /* local aliases → global theme tokens (surface/border/text fall through to :root) */
  --black: var(--bg);
  --white: var(--text-strong);
  --muted: var(--text-muted);
  --faint: var(--text-faint);
  --orange: var(--accent);
  --violet: var(--accent-2);
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;

  position: relative;
  min-height: 100vh;
  background: var(--bg);
  font-family: var(--font-sans);
  color: var(--text);
  overflow: hidden;
}

/* ===== 背景特效 ===== */
.bg-fx {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.bg-grid {
  position: absolute;
  inset: -2px;
  background-image:
    linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: radial-gradient(ellipse 90% 70% at 50% 0%, #000 40%, transparent 100%);
  -webkit-mask-image: radial-gradient(ellipse 90% 70% at 50% 0%, #000 40%, transparent 100%);
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.5;
}

.glow-violet {
  width: 620px;
  height: 620px;
  top: -180px;
  right: -120px;
  background: radial-gradient(circle, rgba(109, 91, 255, 0.55), transparent 70%);
  animation: float-glow 14s ease-in-out infinite;
}

.glow-orange {
  width: 520px;
  height: 520px;
  bottom: -160px;
  left: -120px;
  background: radial-gradient(circle, rgba(255, 90, 44, 0.35), transparent 70%);
  animation: float-glow 18s ease-in-out infinite reverse;
}

@keyframes float-glow {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-40px, 40px); }
}

/* 顶部导航 */
.navbar {
  position: relative;
  z-index: 10;
  height: 64px;
  background: var(--nav-bg);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.1rem;
}

.brand-text {
  background: linear-gradient(90deg, var(--white) 0%, #8b7bff 60%, var(--violet) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
}

.github-link {
  color: var(--text);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.2s;
}

.github-link:hover {
  color: var(--violet);
}

.nav-link-btn {
  color: var(--text);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 500;
  padding: 7px 16px;
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-link-btn:hover {
  background: rgba(109, 91, 255, 0.14);
  border-color: var(--violet);
  box-shadow: 0 0 18px rgba(109, 91, 255, 0.25);
}

.arrow {
  font-family: sans-serif;
}

/* 主要内容区 */
.main-content {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 70px 40px;
}

/* Hero 区域 */
.hero-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 90px;
  position: relative;
  gap: 40px;
}

.hero-left {
  flex: 1;
  padding-right: 20px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.orange-tag {
  background: linear-gradient(90deg, var(--orange), #ff8a3c);
  color: #fff;
  padding: 5px 12px;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 0.72rem;
  border-radius: 4px;
  box-shadow: 0 0 22px rgba(255, 90, 44, 0.45);
}

.version-text {
  color: var(--faint);
  font-weight: 500;
  letter-spacing: 0.5px;
}

.main-title {
  font-size: 4.4rem;
  line-height: 1.12;
  font-weight: 600;
  margin: 0 0 36px 0;
  letter-spacing: -2px;
  color: var(--white);
}

.gradient-text {
  background: linear-gradient(100deg, var(--white) 0%, #8b7bff 45%, var(--violet) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-desc {
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--muted);
  max-width: 640px;
  margin-bottom: 46px;
  font-weight: 400;
  text-align: justify;
}

.hero-desc p {
  margin-bottom: 1.5rem;
}

.highlight-bold {
  color: var(--white);
  font-weight: 700;
}

.highlight-orange {
  color: var(--orange);
  font-weight: 700;
  font-family: var(--font-mono);
}

.highlight-code {
  background: rgba(109, 91, 255, 0.14);
  border: 1px solid rgba(109, 91, 255, 0.3);
  padding: 2px 7px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.9em;
  color: #c3bbff;
  font-weight: 600;
}

.slogan-text {
  font-size: 1.2rem;
  font-weight: 520;
  color: var(--white);
  letter-spacing: 1px;
  border-left: 3px solid var(--orange);
  padding-left: 15px;
  margin-top: 20px;
}

.blinking-cursor {
  color: var(--orange);
  animation: blink 1s step-end infinite;
  font-weight: 700;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.decoration-square {
  width: 16px;
  height: 16px;
  background: var(--orange);
  box-shadow: 0 0 18px rgba(255, 90, 44, 0.6);
}

.hero-right {
  flex: 0.95;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 20px;
}

/* Cubes 视口 */
.cubes-viewport {
  position: relative;
  width: 100%;
  max-width: 480px;
  aspect-ratio: 1 / 1;
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background:
    radial-gradient(circle at 50% 45%, rgba(109, 91, 255, 0.12), transparent 65%),
    rgba(255, 255, 255, 0.015);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  overflow: hidden;
}

.cubes-holder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewport-label {
  position: absolute;
  top: 14px;
  left: 16px;
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 1.5px;
  color: var(--faint);
  z-index: 2;
}

.corner {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 1.5px solid rgba(109, 91, 255, 0.55);
  z-index: 2;
}
.corner.tl { top: 10px; left: 10px; border-right: none; border-bottom: none; }
.corner.tr { top: 10px; right: 10px; border-left: none; border-bottom: none; }
.corner.bl { bottom: 10px; left: 10px; border-right: none; border-top: none; }
.corner.br { bottom: 10px; right: 10px; border-left: none; border-top: none; }

.scroll-down-btn {
  width: 42px;
  height: 42px;
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  background: var(--surface);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--orange);
  font-size: 1.2rem;
  transition: all 0.2s;
}

.scroll-down-btn:hover {
  border-color: var(--orange);
  box-shadow: 0 0 18px rgba(255, 90, 44, 0.3);
  transform: translateY(3px);
}

/* Dashboard 双栏布局 */
.dashboard-section {
  display: flex;
  gap: 50px;
  border-top: 1px solid var(--border);
  padding-top: 60px;
  align-items: flex-start;
}

.dashboard-section .left-panel,
.dashboard-section .right-panel {
  display: flex;
  flex-direction: column;
}

/* 左侧面板 */
.left-panel {
  flex: 0.85;
}

.panel-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.status-dot {
  color: var(--orange);
  font-size: 0.8rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: var(--white);
}

.section-desc {
  color: var(--muted);
  margin-bottom: 25px;
  line-height: 1.6;
}

.metrics-row {
  display: flex;
  gap: 18px;
  margin-bottom: 18px;
}

.metric-card {
  flex: 1;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 12px;
  padding: 20px 26px;
  min-width: 150px;
  transition: all 0.25s;
}

.metric-card:hover {
  border-color: rgba(109, 91, 255, 0.4);
  background: var(--surface-2);
}

.metric-value {
  font-family: var(--font-mono);
  font-size: 1.7rem;
  font-weight: 600;
  margin-bottom: 5px;
  color: var(--white);
}

.metric-label {
  font-size: 0.85rem;
  color: var(--muted);
}

/* 项目模拟步骤介绍 */
.steps-container {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 12px;
  padding: 30px;
  position: relative;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--muted);
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
  color: var(--violet);
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.workflow-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--violet);
  opacity: 0.6;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
  color: var(--white);
}

.step-desc {
  font-size: 0.85rem;
  color: var(--muted);
}

/* 右侧交互控制台 */
.right-panel {
  flex: 1.15;
}

.console-box {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 10px;
  background:
    radial-gradient(circle at 100% 0%, rgba(109, 91, 255, 0.08), transparent 50%),
    var(--surface);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--muted);
}

.upload-zone {
  border: 1px dashed var(--border-strong);
  border-radius: 10px;
  height: 200px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--input-bg);
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover,
.upload-zone.drag-over {
  background: rgba(109, 91, 255, 0.06);
  border-color: var(--violet);
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 44px;
  height: 44px;
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: var(--violet);
  font-size: 1.1rem;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
  color: var(--text);
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--faint);
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--text);
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: var(--muted);
  transition: color 0.2s;
}

.remove-btn:hover {
  color: var(--orange);
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--faint);
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  background: var(--input-bg);
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--violet);
  box-shadow: 0 0 0 3px rgba(109, 91, 255, 0.12);
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
  color: var(--text);
}

.code-input::placeholder {
  color: var(--faint);
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--faint);
}

.start-engine-btn {
  width: 100%;
  background: linear-gradient(100deg, #14141f, #1c1830);
  color: #f3f3fb;
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  padding: 20px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.start-engine-btn:not(:disabled) {
  border-color: rgba(109, 91, 255, 0.5);
  animation: pulse-border 2.4s infinite;
}

.start-engine-btn:hover:not(:disabled) {
  background: linear-gradient(100deg, var(--violet), var(--orange));
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(109, 91, 255, 0.35);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: var(--surface-3);
  color: var(--faint);
  cursor: not-allowed;
  transform: none;
  border-color: var(--border);
}

.user-agent-btn {
  width: 100%;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  padding: 16px 20px;
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
  text-decoration: none;
}

.user-agent-btn:hover {
  background: rgba(109, 91, 255, 0.1);
  border-color: rgba(109, 91, 255, 0.45);
  transform: translateY(-1px);
}

.user-agent-btn:hover .btn-arrow {
  transform: translateX(6px);
}

.btn-arrow {
  transition: transform 0.3s ease;
}

.start-engine-btn:hover:not(:disabled) .btn-arrow {
  transform: translateX(6px);
}

@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(109, 91, 255, 0.4); }
  70% { box-shadow: 0 0 0 8px rgba(109, 91, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(109, 91, 255, 0); }
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .dashboard-section {
    flex-direction: column;
  }

  .hero-section {
    flex-direction: column;
  }

  .hero-left {
    padding-right: 0;
    margin-bottom: 20px;
  }

  .hero-right {
    align-items: stretch;
  }

  .cubes-viewport {
    margin: 0 auto;
  }

  .main-title {
    font-size: 3.4rem;
  }
}
</style>

<style>
/* English locale adjustments (unscoped to target html[lang]) */
html[lang="en"] .main-title {
  font-size: 3.5rem;
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: -1px;
}

html[lang="en"] .hero-desc {
  text-align: left;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: 0;
}

html[lang="en"] .slogan-text {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: 0;
}

html[lang="en"] .tag-row {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .navbar .nav-links {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .workflow-list .step-title {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .workflow-list .step-desc {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  font-size: 0.72rem !important;
  line-height: 1.4 !important;
}

html[lang="en"] .workflow-list {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
