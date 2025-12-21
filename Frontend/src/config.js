// API Configuration
// In development: uses Vite proxy to localhost:5000
// In production (Vercel): calls AWS backend directly

const isDevelopment = import.meta.env.DEV;

const config = {
    // In production, call AWS backend directly
    // In development, use Vite proxy (calls relative URLs)
    API_BASE_URL: isDevelopment ? '' : 'http://51.21.253.28'
};

export default config;
