import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router'
import vuetify from '@/plugins/vuetify'
import App from './App.vue'
import '@/styles/global.css'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Initialize auth from localStorage BEFORE mounting
const authStore = useAuthStore()
authStore.initializeAuth()

app.use(router)
app.use(vuetify)

app.mount('#app')
