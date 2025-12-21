const config = {
    // In development with Vite proxy, these can remain relative
    // In production (Vercel), the rewrites in vercel.json handle the proxying
    // If VITE_API_URL is set, use it; otherwise default to '' which allows Vercel rewrites to work.
    API_BASE_URL: import.meta.env.VITE_API_URL || '',
};

export default config;
