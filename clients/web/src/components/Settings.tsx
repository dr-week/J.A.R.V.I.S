import { useState } from 'react';
import { Server, KeyRound, Check, RefreshCw } from 'lucide-react';

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
    <div className="flex-1 p-5 sm:p-6 rounded-2xl flex flex-col gap-5 overflow-y-auto glass-panel border border-border animate-slide-up">
      <h2 className="text-xl font-semibold m-0 text-foreground">Settings</h2>
      
      <div className="flex flex-col gap-2">
        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
          <Server size={14} className="shrink-0" />
          Brain URL
        </label>
        <input 
          type="text" 
          value={baseUrl} 
          onChange={(e) => setBaseUrl(e.target.value)}
          className="bg-black/35 border border-border text-foreground p-3 rounded-xl text-sm font-sans outline-none focus:border-primary/40 focus:ring-2 focus:ring-primary/20 transition-all"
          placeholder="http://localhost:8787"
        />
        <span className="text-muted-foreground text-xs">The URL where the Jarvis Brain backend is running.</span>
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
          <KeyRound size={14} className="shrink-0" />
          Pairing Secret
        </label>
        <input 
          type="password" 
          value={pairingSecret} 
          onChange={(e) => setPairingSecret(e.target.value)}
          className="bg-black/35 border border-border text-foreground p-3 rounded-xl text-sm font-sans outline-none focus:border-primary/40 focus:ring-2 focus:ring-primary/20 transition-all"
          placeholder="Leave blank to keep current"
        />
        <span className="text-muted-foreground text-xs">Required if pairing fails with 401.</span>
      </div>

      <div className="flex flex-wrap gap-3 mt-3">
        <button 
          className="px-4.5 py-2.5 rounded-xl border-none cursor-pointer font-medium text-sm font-sans transition-all bg-gradient-to-r from-primary to-purple-600 text-white shadow-md shadow-primary/25 hover:opacity-90 flex items-center gap-1.5"
          onClick={handleSave}
        >
          {saved ? <Check size={16} /> : null}
          {saved ? 'Saved!' : 'Save & Reload'}
        </button>
        <button 
          className="px-4.5 py-2.5 rounded-xl border border-destructive/25 cursor-pointer font-medium text-sm font-sans transition-all bg-destructive/10 text-destructive hover:bg-destructive/20 flex items-center gap-1.5"
          onClick={handleClear}
        >
          <RefreshCw size={14} />
          Reset Token & Device ID
        </button>
      </div>
    </div>
  );
}
