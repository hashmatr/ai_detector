import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/predict': 'http://localhost:5000',
            '/predict-file': 'http://localhost:5000',
            '/info': 'http://localhost:5000'
        }
    }
})
