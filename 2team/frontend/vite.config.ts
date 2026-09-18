import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],

  // Frontend에서는 /api만 호출하고, 개발 서버가 FastAPI(8000)로 전달합니다.
  // 이 방식이면 localhost/127.0.0.1 차이로 생기는 CORS 문제도 줄일 수 있습니다.
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
