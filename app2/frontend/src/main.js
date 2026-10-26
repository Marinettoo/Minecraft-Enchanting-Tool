import { createApp } from 'vue'
import { clerkPlugin } from '@clerk/vue'
import { esES } from '@clerk/localizations'
import App from './App.vue'
import './style.css'

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!publishableKey) {
  throw new Error('Falta VITE_CLERK_PUBLISHABLE_KEY en la configuración local.')
}

createApp(App)
  .use(clerkPlugin, {
    publishableKey,
    localization: esES,
    appearance: {
      variables: {
        fontFamily: 'Monocraft, monospace',
        borderRadius: '0px',
        colorPrimary: '#70449a',
        colorBackground: '#f5e8c4',
        colorText: '#382811',
      },
    },
    signInForceRedirectUrl: '/',
    signUpForceRedirectUrl: '/',
  })
  .mount('#app')
