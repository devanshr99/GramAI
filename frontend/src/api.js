import { fallbackSearch } from './offlineDB.js';

// Connect directly to the provided live backend API.
// You can override this in local development by creating a .env in the frontend folder with VITE_API_URL=http://localhost:8000
const API_BASE = import.meta.env.VITE_API_URL || 'https://gramai-0n2o.onrender.com';

export const api = {
  async query(query, category, useLLM, language, mode = 'offline', history = null) {
    const body = { query, category, use_llm: useLLM, language, mode };
    if (mode === 'online' && history) {
      body.history = history.slice(-6).map(m => ({ role: m.role, text: m.text }));
    }
    
    try {
      const res = await fetch(`${API_BASE}/api/chat/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      return await res.json();
    } catch (error) {
      // If there is no internet or backend is down, use the built-in offline database
      console.warn("Network error or zero internet. Falling back to built-in frontend database.", error);
      
      const fallbackResponse = fallbackSearch(query);
      
      return {
        response: fallbackResponse,
        sources: [],
        query: query,
        category: null,
        documents_found: 1,
        language: language,
        mode: 'offline'
      };
    }
  },

  async health() {
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      return res.ok;
    } catch {
      return false;
    }
  },

  async status() {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async onlineStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/chat/online-status`);
      if (!res.ok) return { configured: false, available: false };
      return await res.json();
    } catch { return { configured: false, available: false }; }
  },

  async speak(text) {
    const res = await fetch(`${API_BASE}/api/voice/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error('TTS failed');
    return res.blob();
  },

  async transcribe(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    const res = await fetch(`${API_BASE}/api/voice/transcribe`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('STT failed');
    return res.json();
  },
};
