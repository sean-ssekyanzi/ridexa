import axios from 'axios';

// base URL can be configured via environment variable so the
// frontend can adapt to different ports/hosts (Render, Netlify, etc.).
// Vite exposes vars prefixed with VITE_ to the client.
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || `http://localhost:${import.meta.env.VITE_BACKEND_PORT || 3000}`;

const api = axios.create({
    baseURL: BACKEND_URL,
});


export default api;