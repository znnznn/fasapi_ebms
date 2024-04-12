import react from '@vitejs/plugin-react'
import path from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src')
        }
    },
    server: {
		host: true,
		port: 3000,

		// add the next lines if you're using windows and hot reload doesn't work
		watch: {
			usePolling: true
		}
	},
})
