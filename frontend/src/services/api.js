import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || "https://global-ontology-2.onrender.com";

const API = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,
});

export const addSource = (data) => API.post('/add_source', data);

export const getSources = () => API.get('/sources');

export const deleteSource = (id) => API.delete(`/delete_source/${id}`);

export const toggleSource = (id) => API.patch(`/toggle_source/${id}`);

export const getMonitorData = () => API.get('/monitor');

export const getDashboardStats = () => API.get('/dashboard');

export const sendQuery = (prompt) => API.post('/query', { prompt });

// Intelligence pipeline
export const processSource = (url) => API.post('/process_source', { url });

export const processBulkSources = (domain) => API.post('/process_bulk_sources', { domain });

export const getIntelligenceFeed = () => API.get('/intelligence_feed');

export const deleteIntelligenceEvent = (id) => API.delete(`/intelligence_feed/${id}`);

export default API;

