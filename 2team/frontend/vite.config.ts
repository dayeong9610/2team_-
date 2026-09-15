import react from '@vitejs/plugin-react' // JSX/Fast Refresh 지원을 위한 공식 React 플러그인
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  // React 플러그인만 사용하는 기본 설정
  plugins: [react()],
})

