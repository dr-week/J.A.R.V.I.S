import { useState } from 'react';

export function Settings() {
  const [baseUrl, setBaseUrl] = useState(() => localStorage.getItem('jarvis_brain_url') || 'http://localhost:8787');
  const [pairingSecret, setPairingSecret] = useState(() => localStorage.getItem('jarvis_pairing_secret') || '');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem('jarvis_brain_url', baseUrl);
    if (pairingSecret) {
      localStorage.setItem('jarvis_pairing_secret', pairingSecret);
    }
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      window.location.reload();
    }, 500);
  };

  const handleClear = () => {
    localStorage.removeItem('jarvis_token');
    localStorage.removeItem('jarvis_device_id');
    window.location.reload();
  };

  return (
    <div className="settings-panel glass-panel animate-slide-up">
      <h2 style={{marginTop: 0}}>Settings</h2>
      
      <div className="settings-group">
        <label>Brain URL</label>
        <input 
          type="text" 
          value={baseUrl} 
          onChange={(e) => setBaseUrl(e.target.value)}
          className="settings-input"
          placeholder="http://localhost:8787"
        />
        <small className="settings-hint">The URL where the Jarvis Brain backend is running.</small>
      </div>

      <div className="settings-group">
        <label>Pairing Secret</label>
        <input 
          type="password" 
          value={pairingSecret} 
          onChange={(e) => setPairingSecret(e.target.value)}
          className="settings-input"
          placeholder="Leave blank to keep current"
        />
        <small className="settings-hint">Required if pairing fails with 401.</small>
      </div>

      <div className="settings-actions">
        <button className="settings-btn primary" onClick={handleSave}>
          {saved ? 'Saved!' : 'Save & Reload'}
        </button>
        <button className="settings-btn danger" onClick={handleClear}>
          Reset Token & Device ID
        </button>
      </div>
    </div>
  );
}
