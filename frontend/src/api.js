// Connect directly to the provided live backend API.
// You can override this in local development by creating a .env in the frontend folder with VITE_API_URL=http://localhost:8000
const API_BASE = import.meta.env.VITE_API_URL || 'https://gramai-0n2o.onrender.com';

export const api = {
  async query(query, category, useLLM, language, mode = 'offline', history = null) {
    const body = { query, category, use_llm: useLLM, language, mode };
    if (mode === 'online' && history) {
      body.history = history.slice(-6).map(m => ({ role: m.role, text: m.text }));
    }
    const res = await fetch(`${API_BASE}/api/chat/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    return res.json();
  },

  async health() {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.ok;
  },

  async status() {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) return null;
    return res.json();
  },

  async onlineStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/chat/online-status`);
      if (!res.ok) return { configured: false, available: false };
      return res.json();
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
