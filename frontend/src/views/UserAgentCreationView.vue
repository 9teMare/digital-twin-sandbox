<template>
  <div class="bitget-page">
    <div class="phone-shell">
      <!-- iOS-style status bar -->
      <div class="status-bar">
        <span class="status-time">9:41</span>
        <span class="status-notch" aria-hidden="true"></span>
        <span class="status-icons" aria-hidden="true">
          <span class="sig"></span>
          <span class="wifi"></span>
          <span class="bat"></span>
        </span>
      </div>

      <!-- Intro: Bitget-style home -->
      <template v-if="step === 'intro'">
        <header class="bitget-header">
          <span class="hdr-icon user" aria-hidden="true"></span>
          <div class="search-pill">
            <span class="search-icon" aria-hidden="true"></span>
            <span>{{ $t('userAgentCreation.searchPlaceholder') }}</span>
          </div>
          <span class="hdr-icon headset" aria-hidden="true"></span>
          <span class="hdr-icon bell" aria-hidden="true"></span>
        </header>

        <div class="scroll-body">
          <section class="asset-card">
            <div class="asset-label">
              {{ $t('userAgentCreation.twinTitle') }}
              <span class="eye" aria-hidden="true">👁</span>
            </div>
            <p class="asset-desc">{{ $t('userAgentCreation.twinDesc') }}</p>
            <button type="button" class="pill-btn primary" @click="step = 'profile'">
              {{ $t('userAgentCreation.startBtn') }}
            </button>
          </section>

          <div class="quick-grid">
            <div v-for="item in quickActions" :key="item.label" class="quick-item">
              <span class="quick-icon" aria-hidden="true">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </div>
          </div>

          <section class="promo-banner">
            <div>
              <strong>{{ $t('userAgentCreation.promoTitle') }}</strong>
              <p>{{ $t('userAgentCreation.promoDesc') }}</p>
            </div>
            <span class="promo-emoji" aria-hidden="true">🤖</span>
          </section>

          <section class="market-preview">
            <div class="seg-tabs">
              <span class="seg active">{{ $t('userAgentCreation.tabStandard') }}</span>
              <span class="seg">{{ $t('userAgentCreation.tabVip') }}</span>
            </div>
            <div class="mini-cards">
              <div v-for="card in marketCards" :key="card.name" class="mini-card">
                <span class="mc-name">{{ card.name }}</span>
                <span class="mc-change" :class="card.up ? 'up' : 'down'">{{ card.change }}</span>
              </div>
            </div>
          </section>
        </div>
      </template>

      <!-- Profile: trading prefs (Bitget trade screen feel) -->
      <template v-else-if="step === 'profile'">
        <header class="trade-header">
          <button type="button" class="back-btn" @click="step = 'intro'">‹</button>
          <div class="pair-title">
            <span class="pair">{{ form.main_coin || 'BTC' }}/USDT</span>
            <span class="chev">▾</span>
          </div>
          <span class="trade-hdr-spacer"></span>
        </header>

        <div class="scroll-body profile-body">
          <p class="section-kicker">{{ $t('userAgentCreation.profileKicker') }}</p>
          <h2 class="section-title">{{ $t('userAgentCreation.profileTitle') }}</h2>

          <label class="field-label">{{ $t('userAgentCreation.nickname') }}</label>
          <input v-model="form.name" class="bitget-input" :placeholder="$t('userAgentCreation.nicknamePh')" />

          <label class="field-label">{{ $t('userAgentCreation.mainProduct') }}</label>
          <div class="chip-row">
            <button
              v-for="p in products"
              :key="p.value"
              type="button"
              class="chip-btn"
              :class="{ active: form.main_product === p.value }"
              @click="form.main_product = p.value"
            >
              {{ p.label }}
            </button>
          </div>

          <label class="field-label">{{ $t('userAgentCreation.mainCoin') }}</label>
          <input v-model="form.main_coin" class="bitget-input" placeholder="BTC" />

          <label class="field-label">{{ $t('userAgentCreation.riskPref') }}</label>
          <div class="risk-grid">
            <button
              v-for="r in riskOptions"
              :key="r.value"
              type="button"
              class="risk-btn"
              :class="{ active: form.risk_type === r.value }"
              @click="form.risk_type = r.value"
            >
              <span class="risk-label">{{ r.label }}</span>
              <span class="risk-hint">{{ r.hint }}</span>
            </button>
          </div>

          <button type="button" class="pill-btn primary full" @click="step = 'consent'">
            {{ $t('userAgentCreation.continueBtn') }}
          </button>
        </div>
      </template>

      <!-- Consent -->
      <template v-else-if="step === 'consent'">
        <header class="trade-header">
          <button type="button" class="back-btn" @click="step = 'profile'">‹</button>
          <span class="consent-title">{{ $t('userAgentCreation.consentTitle') }}</span>
          <span class="trade-hdr-spacer"></span>
        </header>

        <div class="scroll-body consent-body">
          <div class="consent-card">
            <h3>{{ $t('userAgentCreation.consentHeading') }}</h3>
            <ul>
              <li v-for="(line, i) in consentLines" :key="i">{{ line }}</li>
            </ul>
          </div>

          <label class="consent-check">
            <input v-model="consentData" type="checkbox" value="twin" />
            <span>{{ $t('userAgentCreation.consentTwin') }}</span>
          </label>
          <label class="consent-check">
            <input v-model="consentData" type="checkbox" value="simulation" />
            <span>{{ $t('userAgentCreation.consentSimulation') }}</span>
          </label>
          <label class="consent-check">
            <input v-model="consentData" type="checkbox" value="privacy" />
            <span>{{ $t('userAgentCreation.consentPrivacy') }}</span>
          </label>

          <p v-if="error" class="error-msg">{{ error }}</p>

          <button
            type="button"
            class="pill-btn primary full trade-cta"
            :disabled="!canSubmit || submitting"
            @click="submitAgent"
          >
            {{ submitting ? $t('userAgentCreation.submitting') : $t('userAgentCreation.consentBtn') }}
          </button>
        </div>
      </template>

      <!-- Success -->
      <template v-else>
        <div class="success-body">
          <div class="success-icon" aria-hidden="true">✓</div>
          <h2>{{ $t('userAgentCreation.successTitle') }}</h2>
          <p>{{ $t('userAgentCreation.successDesc') }}</p>
          <div v-if="createdAgent" class="agent-id-box">
            <span class="id-label">{{ $t('userAgentCreation.agentId') }}</span>
            <span class="id-value">{{ createdAgent.character_id }}</span>
            <span v-if="createdAgent.uid" class="id-sub">UID {{ createdAgent.uid }}</span>
          </div>
          <div v-if="createdAgent" class="exchange-preview">
            <div v-for="row in exchangePreviewRows" :key="row.label" class="preview-row">
              <span class="preview-label">{{ row.label }}</span>
              <span class="preview-value">{{ row.value }}</span>
            </div>
          </div>
          <button type="button" class="pill-btn primary full" @click="router.push('/characters')">
            {{ $t('userAgentCreation.viewLibrary') }}
          </button>
          <button type="button" class="text-btn" @click="resetFlow">
            {{ $t('userAgentCreation.createAnother') }}
          </button>
        </div>
      </template>

      <!-- Bottom nav (decorative) -->
      <nav class="bottom-nav" aria-hidden="true">
        <span v-for="tab in bottomTabs" :key="tab.label" class="nav-item" :class="{ active: tab.active }">
          <span class="nav-ico">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </span>
      </nav>
      <div class="home-indicator" aria-hidden="true"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { createCharacter } from '../api/character'

const router = useRouter()
const { t, tm } = useI18n()

const step = ref('intro')
const submitting = ref(false)
const error = ref('')
const createdAgent = ref(null)
const consentData = ref([])

const form = reactive({
  name: '',
  main_product: 'Spot',
  main_coin: 'BTC',
  risk_type: 'moderate',
})

const products = computed(() => [
  { value: 'Spot', label: t('userAgentCreation.productSpot') },
  { value: 'Futures', label: t('userAgentCreation.productFutures') },
  { value: 'Earn', label: t('userAgentCreation.productEarn') },
])

const riskOptions = computed(() => [
  { value: 'conservative', label: t('userAgentCreation.riskConservative'), hint: t('userAgentCreation.riskConservativeHint') },
  { value: 'moderate', label: t('userAgentCreation.riskModerate'), hint: t('userAgentCreation.riskModerateHint') },
  { value: 'aggressive', label: t('userAgentCreation.riskAggressive'), hint: t('userAgentCreation.riskAggressiveHint') },
  { value: 'degen', label: t('userAgentCreation.riskDegen'), hint: t('userAgentCreation.riskDegenHint') },
])

const quickActions = computed(() => [
  { icon: '🎁', label: t('userAgentCreation.quickWelfare') },
  { icon: '👥', label: t('userAgentCreation.quickInvite') },
  { icon: '🐷', label: t('userAgentCreation.quickEarn') },
  { icon: '📋', label: t('userAgentCreation.quickCopy') },
  { icon: '▦', label: t('userAgentCreation.quickMore') },
])

const marketCards = computed(() => [
  { name: t('userAgentCreation.marketCrypto'), change: '+1.25%', up: true },
  { name: t('userAgentCreation.marketStock'), change: '-0.26%', up: false },
  { name: t('userAgentCreation.marketOnchain'), change: '+9.94%', up: true },
  { name: 'TradFi', change: '+0.14%', up: true },
])

const bottomTabs = computed(() => [
  { icon: '⌂', label: t('userAgentCreation.navHome'), active: step.value === 'intro' },
  { icon: '◔', label: t('userAgentCreation.navMarkets'), active: false },
  { icon: '⇄', label: t('userAgentCreation.navTrade'), active: step.value === 'profile' },
  { icon: '▤', label: t('userAgentCreation.navFutures'), active: false },
  { icon: '◫', label: t('userAgentCreation.navAssets'), active: step.value === 'consent' || step.value === 'success' },
])

const consentLines = computed(() => {
  const lines = tm('userAgentCreation.consentBullets')
  return Array.isArray(lines) ? lines : []
})

const canSubmit = computed(() =>
  consentData.value.includes('twin') &&
  consentData.value.includes('simulation') &&
  consentData.value.includes('privacy') &&
  form.risk_type &&
  form.main_product
)

const USER_SOURCES = ['Website', 'App', 'Referral', 'Partner']

const RISK_PROFILE = {
  conservative: { orders: [40, 220], volume: [800, 4500], vip: [0, 3], positions: [1, 6], feeRate: 0.004 },
  moderate: { orders: [180, 650], volume: [3500, 12000], vip: [2, 5], positions: [3, 12], feeRate: 0.0035 },
  aggressive: { orders: [500, 1200], volume: [8000, 35000], vip: [4, 7], positions: [6, 18], feeRate: 0.0033 },
  degen: { orders: [700, 1800], volume: [12000, 80000], vip: [1, 4], positions: [8, 25], feeRate: 0.003 },
}

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function randFloat(min, max, decimals = 0) {
  const n = min + Math.random() * (max - min)
  return decimals ? Number(n.toFixed(decimals)) : Math.round(n)
}

function pick(arr) {
  return arr[randInt(0, arr.length - 1)]
}

function normalizeCoin(raw) {
  const base = String(raw || 'BTC').trim().toUpperCase().replace(/USDT$/i, '')
  return `${base || 'BTC'}USDT`
}

function productLabel(product) {
  const map = { Spot: 'crypto spot', Futures: 'crypto futures', Earn: 'crypto earn' }
  return map[product] || 'crypto spot'
}

function formatRegisteredAt(date) {
  return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

function randomRegisteredAt() {
  const now = Date.now()
  const daysAgo = randInt(90, 720)
  const d = new Date(now - daysAgo * 86400000)
  d.setHours(randInt(0, 23), pick([7, 12, 15, 19, 2]), 0, 0)
  return formatRegisteredAt(d)
}

function randomActivityIds(count) {
  const ids = []
  let seed = randInt(5018000, 5029000)
  for (let i = 0; i < count; i++) {
    seed += randInt(120, 420)
    ids.push(String(seed))
  }
  return ids
}

/** Build a full exchange-export-style character payload with realistic randomization. */
function buildExchangeCharacterPayload(formValues) {
  const risk = formValues.risk_type || 'moderate'
  const profile = RISK_PROFILE[risk] || RISK_PROFILE.moderate
  const mainCoin = normalizeCoin(formValues.main_coin)
  const mainProduct = productLabel(formValues.main_product)

  const orders30 = randInt(profile.orders[0], profile.orders[1])
  const orders90 = Math.max(orders30 + 1, randInt(Math.round(orders30 * 1.35), Math.round(orders30 * 2.4)))
  const volume30 = randInt(profile.volume[0], profile.volume[1])
  const volume90 = Math.max(volume30 + randInt(500, 3000), randInt(Math.round(volume30 * 1.8), Math.round(volume30 * 4.2)))
  const fees30 = randFloat(volume30 * profile.feeRate * 0.6, volume30 * profile.feeRate * 1.1, 0)
  const fees90 = Math.max(fees30, randFloat(volume90 * profile.feeRate * 0.5, volume90 * profile.feeRate * 0.95, 0))
  const activities90 = randInt(0, 12)
  const activityIds = activities90 > 0 ? randomActivityIds(activities90) : []
  const rewardsClaimed = Math.random() < 0.75 ? 0 : randFloat(5, 120, 2)
  const uid = String(randInt(100000, 99999999))
  const displayName = (formValues.name || '').trim() || `User ${uid}`

  return {
    name: displayName,
    uid,
    user_source: pick(USER_SOURCES),
    registered_at: randomRegisteredAt(),
    vip_level: randInt(profile.vip[0], profile.vip[1]),
    orders_30d: orders30,
    orders_90d: orders90,
    volume_30d: volume30,
    volume_90d: volume90,
    fees_30d: fees30,
    fees_90d: fees90,
    main_product: mainProduct,
    main_coin: mainCoin,
    positions: randInt(profile.positions[0], profile.positions[1]),
    activities_90d: activities90,
    activity_ids: activityIds,
    rewards_claimed: rewardsClaimed,
    risk_type: risk,
    preferred_assets: [mainCoin.replace(/USDT$/i, '')],
    tags: ['user-agent', 'bitget-consent'],
    enabled: true,
    source: 'manual',
    bio: t('userAgentCreation.autoBio', { product: mainProduct, coin: mainCoin, risk }),
  }
}

const exchangePreviewRows = computed(() => {
  const a = createdAgent.value
  if (!a) return []
  const activityIds = Array.isArray(a.activity_ids) ? a.activity_ids.join(';') : (a.activity_ids || '—')
  return [
    { label: 'UID', value: a.uid },
    { label: t('characters.fUserSource'), value: a.user_source },
    { label: t('characters.fRegisteredAt'), value: a.registered_at },
    { label: t('characters.fVipLevel'), value: a.vip_level },
    { label: t('characters.fOrders30d'), value: a.orders_30d?.toLocaleString?.() ?? a.orders_30d },
    { label: t('characters.fOrders90d'), value: a.orders_90d?.toLocaleString?.() ?? a.orders_90d },
    { label: t('characters.fVolume30d'), value: a.volume_30d?.toLocaleString?.() ?? a.volume_30d },
    { label: t('characters.fVolume90d'), value: a.volume_90d?.toLocaleString?.() ?? a.volume_90d },
    { label: t('characters.fMainProduct'), value: a.main_product },
    { label: t('characters.fMainCoin'), value: a.main_coin },
    { label: t('characters.fPositions'), value: a.positions },
    { label: t('characters.fActivities90d'), value: a.activities_90d },
    { label: t('characters.fActivityIds'), value: activityIds || '—' },
  ]
})

function resetFlow() {
  step.value = 'intro'
  createdAgent.value = null
  consentData.value = []
  error.value = ''
  form.name = ''
  form.main_product = 'Spot'
  form.main_coin = 'BTC'
  form.risk_type = 'moderate'
}

async function submitAgent() {
  if (!canSubmit.value || submitting.value) return
  submitting.value = true
  error.value = ''

  try {
    const payload = buildExchangeCharacterPayload(form)
    const res = await createCharacter(payload)

    if (res.success && res.data) {
      createdAgent.value = res.data
      step.value = 'success'
    } else {
      error.value = res.error || t('userAgentCreation.errCreate')
    }
  } catch (e) {
    error.value = e.message || t('userAgentCreation.errCreate')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.bitget-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background: #e8eaed;
}

.phone-shell {
  position: relative;
  width: 100%;
  max-width: 390px;
  min-height: 780px;
  max-height: 90vh;
  background: #fff;
  border-radius: 36px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.18), 0 0 0 1px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: #111;
}

.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 22px 6px;
  font-size: 15px;
  font-weight: 600;
  flex-shrink: 0;
}

.status-notch {
  width: 120px;
  height: 28px;
  background: #111;
  border-radius: 20px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  top: 10px;
}

.status-icons {
  display: flex;
  gap: 5px;
  font-size: 12px;
}

.bitget-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px 12px;
  flex-shrink: 0;
}

.hdr-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #f0f0f0;
  flex-shrink: 0;
}

.search-pill {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f5f5f5;
  border-radius: 999px;
  padding: 10px 14px;
  font-size: 14px;
  color: #999;
}

.search-icon {
  width: 14px;
  height: 14px;
  border: 2px solid #bbb;
  border-radius: 50%;
  position: relative;
}

.scroll-body {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
  -webkit-overflow-scrolling: touch;
}

.asset-card {
  padding: 4px 0 20px;
}

.asset-label {
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 6px;
}

.asset-desc {
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  margin: 10px 0 16px;
}

.pill-btn {
  border: none;
  border-radius: 999px;
  padding: 12px 28px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.pill-btn.primary {
  background: #111;
  color: #fff;
}

.pill-btn.primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.pill-btn.full {
  width: 100%;
  margin-top: 8px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #333;
  text-align: center;
}

.quick-icon {
  font-size: 22px;
}

.promo-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(90deg, #f8f8f8, #fff5f0);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 20px;
  font-size: 13px;
}

.promo-banner p {
  margin: 4px 0 0;
  color: #666;
  font-size: 12px;
}

.promo-emoji {
  font-size: 36px;
}

.seg-tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 15px;
}

.seg {
  color: #999;
  padding-bottom: 6px;
}

.seg.active {
  color: #111;
  font-weight: 700;
  border-bottom: 2px solid #111;
}

.mini-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding-bottom: 12px;
}

.mini-card {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 12px;
}

.mc-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

.mc-change {
  font-size: 13px;
  font-weight: 600;
}

.mc-change.up { color: #00b4a0; }
.mc-change.down { color: #e05252; }

.trade-header {
  display: flex;
  align-items: center;
  padding: 8px 12px 12px;
  gap: 8px;
  flex-shrink: 0;
  border-bottom: 1px solid #f0f0f0;
}

.back-btn {
  border: none;
  background: none;
  font-size: 28px;
  line-height: 1;
  padding: 0 8px;
  cursor: pointer;
  color: #111;
}

.pair-title {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 17px;
  font-weight: 700;
}

.chev {
  font-size: 12px;
  color: #666;
}

.consent-title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 700;
}

.trade-hdr-spacer {
  width: 44px;
}

.profile-body,
.consent-body {
  padding-top: 16px;
  padding-bottom: 24px;
}

.section-kicker {
  font-size: 12px;
  color: #00b4a0;
  font-weight: 600;
  margin: 0 0 4px;
}

.section-title {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 20px;
  line-height: 1.25;
}

.field-label {
  display: block;
  font-size: 13px;
  color: #666;
  margin: 14px 0 8px;
}

.bitget-input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 15px;
  background: #fafafa;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-btn {
  border: 1px solid #e0e0e0;
  background: #fff;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}

.chip-btn.active {
  background: #111;
  color: #fff;
  border-color: #111;
}

.risk-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.risk-btn {
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 12px;
  text-align: left;
  background: #fafafa;
  cursor: pointer;
}

.risk-btn.active {
  border-color: #00b4a0;
  background: #f0fffc;
  box-shadow: 0 0 0 1px #00b4a0;
}

.risk-label {
  display: block;
  font-size: 14px;
  font-weight: 700;
  text-transform: capitalize;
}

.risk-hint {
  display: block;
  font-size: 11px;
  color: #888;
  margin-top: 4px;
  line-height: 1.3;
}

.consent-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid #eee;
}

.consent-card h3 {
  margin: 0 0 12px;
  font-size: 15px;
}

.consent-card ul {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.55;
  color: #444;
}

.consent-check {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  line-height: 1.45;
  margin-bottom: 14px;
  cursor: pointer;
}

.consent-check input {
  margin-top: 3px;
  accent-color: #111;
}

.trade-cta {
  padding: 16px;
  font-size: 16px;
  margin-top: 12px;
}

.error-msg {
  color: #c62828;
  font-size: 13px;
  margin: 8px 0 0;
}

.success-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  text-align: center;
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #00b4a0;
  color: #fff;
  font-size: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.success-body h2 {
  margin: 0 0 10px;
  font-size: 22px;
}

.success-body p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 20px;
}

.agent-id-box {
  width: 100%;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.id-label {
  display: block;
  font-size: 11px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.id-value {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  margin-top: 6px;
  word-break: break-all;
}

.id-sub {
  display: block;
  font-size: 12px;
  color: #666;
  margin-top: 6px;
}

.exchange-preview {
  width: 100%;
  max-height: 220px;
  overflow-y: auto;
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 16px;
  text-align: left;
}

.preview-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 11px;
}

.preview-row:last-child {
  border-bottom: none;
}

.preview-label {
  color: #888;
  flex-shrink: 0;
}

.preview-value {
  color: #111;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  text-align: right;
  word-break: break-all;
}

.text-btn {
  border: none;
  background: none;
  color: #666;
  font-size: 14px;
  margin-top: 12px;
  cursor: pointer;
  text-decoration: underline;
}

.bottom-nav {
  display: flex;
  justify-content: space-around;
  padding: 8px 8px 4px;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0;
  background: #fff;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-size: 10px;
  color: #999;
  min-width: 52px;
}

.nav-item.active {
  color: #111;
  font-weight: 600;
}

.nav-ico {
  font-size: 18px;
}

.home-indicator {
  width: 120px;
  height: 4px;
  background: #111;
  border-radius: 4px;
  margin: 6px auto 8px;
  flex-shrink: 0;
}
</style>
