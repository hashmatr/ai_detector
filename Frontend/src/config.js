const config = {
    // In development with Vite proxy, these can remain relative. 
    // In production, we need the full URL if the backend is on a different domain.
    // We'll use an environment variable for the backend URL.
    // If VITE_API_URL is set, use it; otherwise default to '' which allows Vercel rewrites to work.
    API_BASE_URL: import.meta.env.VITE_API_URL || '',
};

export default config;
