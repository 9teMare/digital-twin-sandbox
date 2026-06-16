<template>
  <div class="characters-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/')">DIGITAL TWIN AGENT SANDBOX</div>
        <span class="page-tag">{{ $t('characters.title') }}</span>
      </div>
      <div class="header-right">
        <ThemeSwitcher />
        <LanguageSwitcher />
      </div>
    </header>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <input
          v-model="filters.q"
          class="search-input"
          :placeholder="$t('characters.searchPlaceholder')"
          @keyup.enter="reload"
        />
        <select v-model="filters.tag" class="filter-select" @change="reload">
          <option value="">{{ $t('characters.allTags') }}</option>
          <option v-for="tg in allTags" :key="tg" :value="tg">{{ tg }}</option>
        </select>
        <select v-model="filters.enabled" class="filter-select" @change="reload">
          <option value="">{{ $t('characters.allStatus') }}</option>
          <option value="true">{{ $t('characters.enabled') }}</option>
          <option value="false">{{ $t('characters.disabled') }}</option>
        </select>
      </div>
      <div class="toolbar-right">
        <button class="btn ghost" @click="reload">{{ $t('characters.refresh') }}</button>
        <button class="btn ghost" @click="openImport">{{ $t('characters.import') }}</button>
        <a class="btn ghost" :href="exportUrl" target="_blank" rel="noopener">{{ $t('characters.export') }}</a>
        <button class="btn primary" @click="openCreate">+ {{ $t('characters.newCharacter') }}</button>
      </div>
    </div>

    <!-- Table -->
    <main class="content">
      <div v-if="loading" class="state-msg">{{ $t('characters.loading') }}</div>
      <div v-else-if="characters.length === 0" class="state-msg empty">
        <div class="empty-title">{{ $t('characters.emptyTitle') }}</div>
        <div class="empty-desc">{{ $t('characters.emptyDesc') }}</div>
        <button class="btn primary" @click="openCreate">+ {{ $t('characters.newCharacter') }}</button>
      </div>
      <table v-else class="grid">
        <thead>
          <tr>
            <th>{{ $t('characters.fName') }}</th>
            <th>{{ $t('characters.fAge') }}</th>
            <th>{{ $t('characters.fOccupation') }}</th>
            <th>{{ $t('characters.fRiskType') }}</th>
            <th>{{ $t('characters.fPurpose') }}</th>
            <th>{{ $t('characters.fAssets') }}</th>
            <th>{{ $t('characters.fStatus') }}</th>
            <th class="actions-col">{{ $t('characters.fActions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in characters" :key="c.character_id">
            <td class="name-cell">{{ c.name }}</td>
            <td>{{ c.age ?? '—' }}</td>
            <td>{{ c.occupation || '—' }}</td>
            <td><span v-if="c.risk_type" class="chip" :class="riskClass(c.risk_type)">{{ c.risk_type }}</span><span v-else>—</span></td>
            <td>{{ c.purpose || '—' }}</td>
            <td>
              <span v-for="a in (c.preferred_assets || []).slice(0, 3)" :key="a" class="chip asset">{{ a }}</span>
              <span v-if="(c.preferred_assets || []).length > 3" class="more">+{{ c.preferred_assets.length - 3 }}</span>
              <span v-if="!(c.preferred_assets || []).length">—</span>
            </td>
            <td>
              <button class="toggle" :class="{ on: c.enabled }" @click="toggleEnabled(c)">
                {{ c.enabled ? $t('characters.enabled') : $t('characters.disabled') }}
              </button>
            </td>
            <td class="actions-col">
              <button class="icon-btn" @click="openEdit(c)" :title="$t('characters.edit')">✎</button>
              <button class="icon-btn danger" @click="removeCharacter(c)" :title="$t('characters.delete')">🗑</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="!loading && total > 0" class="pagination">
        <span class="page-info">{{ rangeStart }}–{{ rangeEnd }} / {{ total }}</span>
        <button class="btn ghost sm" :disabled="filters.offset === 0" @click="prevPage">‹</button>
        <button class="btn ghost sm" :disabled="rangeEnd >= total" @click="nextPage">›</button>
      </div>
    </main>

    <!-- Edit / Create Drawer -->
    <div v-if="drawerOpen" class="drawer-mask" @click.self="closeDrawer">
      <aside class="drawer">
        <div class="drawer-header">
          <h3>{{ editingId ? $t('characters.editTitle') : $t('characters.createTitle') }}</h3>
          <button class="icon-btn" @click="closeDrawer">×</button>
        </div>
        <div class="drawer-body">
          <fieldset>
            <legend>{{ $t('characters.secIdentity') }}</legend>
            <div class="field"><label>{{ $t('characters.fName') }} *</label><input v-model="form.name" /></div>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fAge') }}</label><input v-model.number="form.age" type="number" min="0" /></div>
              <div class="field"><label>{{ $t('characters.fGender') }}</label>
                <select v-model="form.gender"><option value="">—</option><option v-for="o in opts.gender" :key="o" :value="o">{{ o }}</option></select>
              </div>
            </div>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fOccupation') }}</label><input v-model="form.occupation" /></div>
              <div class="field"><label>{{ $t('characters.fJurisdiction') }}</label><input v-model="form.jurisdiction" /></div>
            </div>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fSourceOfIncome') }}</label><input v-model="form.source_of_income" /></div>
              <div class="field"><label>{{ $t('characters.fKycTier') }}</label><input v-model="form.kyc_tier" /></div>
            </div>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fIncomeBand') }}</label><input v-model="form.income_band" /></div>
              <div class="field"><label>{{ $t('characters.fNetWorthBand') }}</label><input v-model="form.net_worth_band" /></div>
            </div>
          </fieldset>

          <fieldset>
            <legend>{{ $t('characters.secRisk') }}</legend>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fRiskType') }}</label>
                <select v-model="form.risk_type"><option value="">—</option><option v-for="o in opts.risk_type" :key="o" :value="o">{{ o }}</option></select>
              </div>
              <div class="field"><label>{{ $t('characters.fExperience') }}</label>
                <select v-model="form.experience_level"><option value="">—</option><option v-for="o in opts.experience_level" :key="o" :value="o">{{ o }}</option></select>
              </div>
            </div>
            <div class="field"><label>{{ $t('characters.fPurpose') }}</label>
              <select v-model="form.purpose"><option value="">—</option><option v-for="o in opts.purpose" :key="o" :value="o">{{ o }}</option></select>
            </div>
          </fieldset>

          <fieldset>
            <legend>{{ $t('characters.secTrading') }}</legend>
            <div class="field"><label>{{ $t('characters.fAssets') }}</label><input v-model="preferredAssetsText" :placeholder="$t('characters.commaHint')" /></div>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fHoldingStyle') }}</label>
                <select v-model="form.holding_style"><option value="">—</option><option v-for="o in opts.holding_style" :key="o" :value="o">{{ o }}</option></select>
              </div>
              <div class="field"><label>{{ $t('characters.fFrequency') }}</label><input v-model="form.trading_frequency" /></div>
            </div>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fPositionSize') }}</label><input v-model="form.avg_position_size" /></div>
              <div class="field"><label>{{ $t('characters.fLeverage') }}</label>
                <select v-model="form.leverage_usage"><option value="">—</option><option v-for="o in opts.leverage_usage" :key="o" :value="o">{{ o }}</option></select>
              </div>
            </div>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fDerivatives') }}</label><input v-model="form.derivatives_usage" /></div>
              <div class="field"><label>{{ $t('characters.fDepositPattern') }}</label><input v-model="form.deposit_withdrawal_pattern" /></div>
            </div>
            <div class="field"><label>{{ $t('characters.fVolatilityReaction') }}</label><input v-model="form.reaction_to_volatility" /></div>
          </fieldset>

          <fieldset>
            <legend>{{ $t('characters.secPsych') }}</legend>
            <div class="row2">
              <div class="field"><label>{{ $t('characters.fSentiment') }}</label>
                <select v-model="form.sentiment_bias"><option value="">—</option><option v-for="o in opts.sentiment_bias" :key="o" :value="o">{{ o }}</option></select>
              </div>
              <div class="field"><label>{{ $t('characters.fFomo') }}</label>
                <select v-model="form.fomo_susceptibility"><option value="">—</option><option v-for="o in opts.fomo_susceptibility" :key="o" :value="o">{{ o }}</option></select>
              </div>
            </div>
            <div class="field"><label>{{ $t('characters.fSocialInfluence') }}</label><input v-model="form.social_influence" /></div>
            <div class="field"><label>{{ $t('characters.fBio') }}</label><textarea v-model="form.bio" rows="2"></textarea></div>
            <div class="field"><label>{{ $t('characters.fPersona') }}</label><textarea v-model="form.persona" rows="4" :placeholder="$t('characters.personaHint')"></textarea></div>
          </fieldset>

          <fieldset>
            <legend>{{ $t('characters.secMeta') }}</legend>
            <div class="field"><label>{{ $t('characters.fTags') }}</label><input v-model="tagsText" :placeholder="$t('characters.commaHint')" /></div>
            <label class="checkbox"><input type="checkbox" v-model="form.enabled" /> {{ $t('characters.fEnabled') }}</label>
            <label class="checkbox"><input type="checkbox" v-model="form.zep_enrich" /> {{ $t('characters.fZepEnrich') }}</label>
            <p class="hint">{{ $t('characters.zepHint') }}</p>
            <div v-if="form.zep_enrich" class="field">
              <label>{{ $t('characters.fTradingHistory') }}</label>
              <textarea v-model="form.trading_history" rows="4" :placeholder="$t('characters.historyHint')"></textarea>
            </div>
          </fieldset>
        </div>
        <div class="drawer-footer">
          <button class="btn ghost" @click="closeDrawer">{{ $t('characters.cancel') }}</button>
          <button class="btn primary" :disabled="saving || !form.name" @click="save">{{ saving ? $t('characters.saving') : $t('characters.save') }}</button>
        </div>
      </aside>
    </div>

    <!-- Import Modal -->
    <div v-if="importOpen" class="modal-mask" @click.self="importOpen = false">
      <div class="modal">
        <div class="drawer-header">
          <h3>{{ $t('characters.importTitle') }}</h3>
          <button class="icon-btn" @click="importOpen = false">×</button>
        </div>
        <div class="modal-body">
          <p class="hint">{{ $t('characters.importDesc') }}</p>
          <input ref="fileInput" type="file" accept=".csv,.json" @change="onFileChange" />
          <div class="or">{{ $t('characters.or') }}</div>
          <textarea v-model="pasteText" rows="6" :placeholder="$t('characters.pastePlaceholder')"></textarea>
        </div>
        <div class="drawer-footer">
          <button class="btn ghost" @click="importOpen = false">{{ $t('characters.cancel') }}</button>
          <button class="btn primary" :disabled="importing" @click="doImport">{{ importing ? $t('characters.importing') : $t('characters.import') }}</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'
import {
  listCharacters, createCharacter, updateCharacter, deleteCharacter,
  importCharactersFile, importCharactersData, exportCharactersUrl
} from '../api/character'

const router = useRouter()
const { t } = useI18n()

const opts = {
  gender: ['male', 'female', 'other'],
  risk_type: ['conservative', 'moderate', 'aggressive', 'degen'],
  purpose: ['investment', 'speculation', 'active_trading', 'payments', 'yield', 'hedging'],
  experience_level: ['beginner', 'intermediate', 'advanced', 'professional'],
  holding_style: ['hodler', 'swing', 'day', 'scalper'],
  leverage_usage: ['none', 'low', 'medium', 'high'],
  sentiment_bias: ['bullish', 'bearish', 'neutral'],
  fomo_susceptibility: ['low', 'medium', 'high']
}

const PAGE_SIZE = 25
const characters = ref([])
const allTags = ref([])
const total = ref(0)
const loading = ref(false)
const filters = reactive({ q: '', tag: '', enabled: '', offset: 0 })

const exportUrl = exportCharactersUrl()

const rangeStart = computed(() => (total.value === 0 ? 0 : filters.offset + 1))
const rangeEnd = computed(() => Math.min(filters.offset + PAGE_SIZE, total.value))

const toast = reactive({ show: false, msg: '', type: 'ok' })
let toastTimer = null
function notify(msg, type = 'ok') {
  toast.msg = msg; toast.type = type; toast.show = true
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.show = false }, 2600)
}

function riskClass(risk) {
  return {
    conservative: 'risk-low', moderate: 'risk-mid',
    aggressive: 'risk-high', degen: 'risk-max'
  }[risk] || ''
}

async function load() {
  loading.value = true
  try {
    const params = { limit: PAGE_SIZE, offset: filters.offset }
    if (filters.q) params.q = filters.q
    if (filters.tag) params.tag = filters.tag
    if (filters.enabled !== '') params.enabled = filters.enabled
    const res = await listCharacters(params)
    characters.value = res.data.characters
    total.value = res.data.total
    allTags.value = res.data.all_tags || []
  } catch (e) {
    notify(t('characters.errLoad'), 'err')
  } finally {
    loading.value = false
  }
}

function reload() { filters.offset = 0; load() }
function prevPage() { filters.offset = Math.max(0, filters.offset - PAGE_SIZE); load() }
function nextPage() { filters.offset += PAGE_SIZE; load() }

// ---------- Drawer / form ----------
const drawerOpen = ref(false)
const editingId = ref(null)
const saving = ref(false)
const form = reactive(blankForm())

function blankForm() {
  return {
    name: '', age: null, gender: '', occupation: '', jurisdiction: '',
    source_of_income: '', income_band: '', net_worth_band: '', kyc_tier: '',
    risk_type: '', purpose: '', experience_level: '',
    preferred_assets: [], avg_position_size: '', trading_frequency: '',
    holding_style: '', leverage_usage: '', derivatives_usage: '',
    reaction_to_volatility: '', deposit_withdrawal_pattern: '',
    sentiment_bias: '', fomo_susceptibility: '', social_influence: '',
    bio: '', persona: '', tags: [], enabled: true,
    zep_enrich: false, trading_history: ''
  }
}

function setForm(data) {
  Object.assign(form, blankForm(), data)
  form.preferred_assets = data.preferred_assets || []
  form.tags = data.tags || []
}

const preferredAssetsText = computed({
  get: () => (form.preferred_assets || []).join(', '),
  set: (v) => { form.preferred_assets = splitList(v) }
})
const tagsText = computed({
  get: () => (form.tags || []).join(', '),
  set: (v) => { form.tags = splitList(v) }
})
function splitList(v) {
  return String(v).split(',').map(s => s.trim()).filter(Boolean)
}

function openCreate() { editingId.value = null; setForm(blankForm()); drawerOpen.value = true }
function openEdit(c) { editingId.value = c.character_id; setForm(c); drawerOpen.value = true }
function closeDrawer() { drawerOpen.value = false }

async function save() {
  if (!form.name) return
  saving.value = true
  try {
    const payload = JSON.parse(JSON.stringify(form))
    if (editingId.value) {
      await updateCharacter(editingId.value, payload)
      notify(t('characters.savedOk'))
    } else {
      await createCharacter(payload)
      notify(t('characters.createdOk'))
    }
    drawerOpen.value = false
    load()
  } catch (e) {
    notify(t('characters.errSave'), 'err')
  } finally {
    saving.value = false
  }
}

async function toggleEnabled(c) {
  try {
    await updateCharacter(c.character_id, { enabled: !c.enabled })
    c.enabled = !c.enabled
  } catch (e) {
    notify(t('characters.errSave'), 'err')
  }
}

async function removeCharacter(c) {
  if (!window.confirm(t('characters.confirmDelete', { name: c.name }))) return
  try {
    await deleteCharacter(c.character_id)
    notify(t('characters.deletedOk'))
    if (characters.value.length === 1 && filters.offset > 0) {
      filters.offset = Math.max(0, filters.offset - PAGE_SIZE)
    }
    load()
  } catch (e) {
    notify(t('characters.errDelete'), 'err')
  }
}

// ---------- Import ----------
const importOpen = ref(false)
const importing = ref(false)
const pasteText = ref('')
const fileInput = ref(null)
let selectedFile = null

function openImport() { pasteText.value = ''; selectedFile = null; importOpen.value = true }
function onFileChange(e) { selectedFile = e.target.files[0] || null }

async function doImport() {
  importing.value = true
  try {
    let res
    if (selectedFile) {
      res = await importCharactersFile(selectedFile)
    } else if (pasteText.value.trim()) {
      const text = pasteText.value.trim()
      if (text.startsWith('[') || text.startsWith('{')) {
        const parsed = JSON.parse(text)
        res = await importCharactersData({ characters: Array.isArray(parsed) ? parsed : [parsed] })
      } else {
        res = await importCharactersData({ csv: text })
      }
    } else {
      notify(t('characters.errNoImport'), 'err')
      importing.value = false
      return
    }
    notify(t('characters.importedOk', { n: res.data.imported }))
    importOpen.value = false
    reload()
  } catch (e) {
    notify(t('characters.errImport'), 'err')
  } finally {
    importing.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.characters-view {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

.app-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 28px; border-bottom: 1px solid var(--border);
}
.header-left { display: flex; align-items: center; gap: 14px; }
.brand { font-weight: 700; letter-spacing: 0.5px; cursor: pointer; font-size: 15px; }
.page-tag {
  font-family: 'JetBrains Mono', monospace; font-size: 12px;
  background: #FFF1EC; color: #FF5722; padding: 3px 10px; border-radius: 4px;
}

.toolbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 16px 28px; flex-wrap: wrap;
}
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 10px; }
.search-input {
  width: 280px; padding: 9px 12px; border: 1px solid var(--border); border-radius: 6px;
  font-size: 13px;
}
.filter-select { padding: 9px 10px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; background: var(--input-bg); }

.btn {
  padding: 9px 16px; border-radius: 6px; font-size: 13px; cursor: pointer;
  border: 1px solid transparent; font-family: inherit; text-decoration: none;
  display: inline-flex; align-items: center; transition: all .15s;
}
.btn.sm { padding: 4px 10px; }
.btn.primary { background: #FF5722; color: #FFF; }
.btn.primary:hover { background: #E64A19; }
.btn.primary:disabled { background: #FFB59E; cursor: not-allowed; }
.btn.ghost { background: var(--surface); border-color: var(--border); color: var(--text); }
.btn.ghost:hover { background: var(--bg-muted); }
.btn.ghost:disabled { color: #BBB; cursor: not-allowed; }

.content { padding: 0 28px 40px; }
.state-msg { padding: 60px; text-align: center; color: var(--text-faint); font-family: 'JetBrains Mono', monospace; }
.state-msg.empty { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.empty-title { font-size: 18px; font-weight: 600; color: var(--text); }
.empty-desc { color: var(--text-faint); margin-bottom: 8px; }

.grid { width: 100%; border-collapse: collapse; font-size: 13px; }
.grid th {
  text-align: left; padding: 12px 14px; border-bottom: 2px solid var(--border);
  font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase;
  color: var(--text-faint); letter-spacing: 0.5px;
}
.grid td { padding: 12px 14px; border-bottom: 1px solid var(--border-subtle); }
.grid tbody tr:hover { background: var(--bg-subtle); }
.name-cell { font-weight: 600; }
.actions-col { text-align: right; width: 90px; }

.chip {
  display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px;
  margin-right: 4px; font-family: 'JetBrains Mono', monospace;
}
.chip.asset { background: var(--bg-muted); color: var(--text-muted); }
.chip.risk-low { background: #E8F5E9; color: #2E7D32; }
.chip.risk-mid { background: #FFF8E1; color: #F57F17; }
.chip.risk-high { background: #FFEBEE; color: #C62828; }
.chip.risk-max { background: #1A1A1A; color: #FF5722; }
.more { color: var(--text-faint); font-size: 11px; }

.toggle {
  border: 1px solid var(--border); background: var(--bg-subtle); color: var(--text-faint);
  padding: 3px 10px; border-radius: 12px; font-size: 11px; cursor: pointer;
  font-family: 'JetBrains Mono', monospace;
}
.toggle.on { background: #E8F5E9; border-color: #A5D6A7; color: #2E7D32; }

.icon-btn {
  background: none; border: none; cursor: pointer; font-size: 15px;
  padding: 4px 6px; border-radius: 4px; color: var(--text-muted);
}
.icon-btn:hover { background: var(--bg-muted); }
.icon-btn.danger:hover { background: #FFEBEE; }

.pagination { display: flex; align-items: center; justify-content: flex-end; gap: 8px; margin-top: 16px; }
.page-info { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-faint); }

/* Drawer */
.drawer-mask { position: fixed; inset: 0; background: var(--overlay); z-index: 50; }
.drawer {
  position: absolute; right: 0; top: 0; bottom: 0; width: 560px; max-width: 92vw;
  background: var(--elevated); display: flex; flex-direction: column; box-shadow: -4px 0 24px rgba(0,0,0,0.12);
}
.drawer-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 22px; border-bottom: 1px solid var(--border);
}
.drawer-header h3 { margin: 0; font-size: 16px; }
.drawer-body { padding: 18px 22px; overflow-y: auto; flex: 1; }
.drawer-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 22px; border-top: 1px solid var(--border);
}

fieldset { border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; margin-bottom: 16px; }
legend {
  padding: 0 8px; font-family: 'JetBrains Mono', monospace; font-size: 11px;
  text-transform: uppercase; color: #FF5722; letter-spacing: 0.5px;
}
.field { margin-bottom: 12px; }
.field label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 5px; }
.field input, .field select, .field textarea {
  width: 100%; padding: 8px 10px; border: 1px solid var(--border); border-radius: 6px;
  font-size: 13px; font-family: inherit; box-sizing: border-box; background: var(--input-bg);
}
.field textarea { resize: vertical; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.checkbox { display: flex; align-items: center; gap: 8px; font-size: 13px; margin-bottom: 8px; }
.hint { font-size: 12px; color: var(--text-faint); margin: 4px 0 10px; }

/* Modal */
.modal-mask { position: fixed; inset: 0; background: var(--overlay); z-index: 60; display: flex; align-items: center; justify-content: center; }
.modal { width: 520px; max-width: 92vw; background: var(--elevated); border-radius: 10px; display: flex; flex-direction: column; }
.modal-body { padding: 18px 22px; }
.modal-body input[type=file] { display: block; margin-bottom: 14px; }
.modal-body textarea { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 12px; box-sizing: border-box; }
.or { text-align: center; color: #BBB; font-size: 12px; margin: 8px 0; font-family: 'JetBrains Mono', monospace; }

/* Toast */
.toast {
  position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%);
  padding: 12px 22px; border-radius: 8px; font-size: 13px; z-index: 80;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.toast.ok { background: #1A1A1A; color: #FFF; }
.toast.err { background: #C62828; color: #FFF; }
.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
