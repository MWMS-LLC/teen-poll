// src/lib/api.ts
import axios from "axios";

// Create one shared axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE, // comes from .env.production or .env.development
  withCredentials: false, // we’re not sending cookies/sessions
});

export default api;
