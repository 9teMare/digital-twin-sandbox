import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './styles/theme.css'
import { useTheme } from './store/theme.js'

// Apply persisted/system theme before mount to avoid a flash
useTheme().initTheme()

const app = createApp(App)

app.use(router)
app.use(i18n)

app.mount('#app')
