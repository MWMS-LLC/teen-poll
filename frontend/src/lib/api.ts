// src/lib/api.ts
import axios from "axios";
import API_BASE from '../config.js';

// Create one shared axios instance
const api = axios.create({
  baseURL: API_BASE, // hardcoded for reliability
  withCredentials: false, // we're not sending cookies/sessions
});

export default api;
