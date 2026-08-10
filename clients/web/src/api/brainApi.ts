export interface HealthInfo {
  status: string;
  version: string;
  assistant_name: string;
  llm_ready: boolean;
}

export interface PairResponse {
  token: string;
}

export interface SessionInfo {
  id: string;
  title: string;
  updated_at: string;
  created_at: string;
}

export interface SessionData {
  ok: boolean;
  session: SessionInfo;
  messages: {
    role: string;
    content: string;
    ts: string;
  }[];
}

class BrainApi {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8787') {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  private get headers(): Record<string, string> {
    const h: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      h['Authorization'] = `Bearer ${this.token}`;
    }
    return h;
  }

  async health(): Promise<HealthInfo> {
    const res = await fetch(`${this.baseUrl}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
  }

  async pair(deviceId: string, deviceName = 'web'): Promise<string> {
    const res = await fetch(`${this.baseUrl}/pair`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pairing_secret: 'change-me-to-something-random', // Using default from .env.example
        device_id: deviceId,
        device_name: deviceName,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Pairing failed: ${res.status} ${await res.text()}`);
    }
    
    const data = await res.json() as PairResponse;
    if (!data.token) {
      throw new Error('Pairing response missing token');
    }
    this.setToken(data.token);
    return data.token;
  }

  async listSessions(): Promise<SessionInfo[]> {
    const res = await fetch(`${this.baseUrl}/sessions`, {
      headers: this.headers,
    });
    if (!res.ok) throw new Error(`Failed to list sessions: ${res.status}`);
    const data = await res.json();
    return data.sessions || [];
  }

  async getSession(sessionId: string): Promise<SessionData> {
    const res = await fetch(`${this.baseUrl}/sessions/${sessionId}`, {
      headers: this.headers,
    });
    if (!res.ok) throw new Error(`Failed to fetch session: ${res.status}`);
    return res.json();
  }

  async streamChat(
    text: string,
    sessionId: string,
    deviceId: string,
    onPartial: (text: string) => void
  ): Promise<string> {
    const res = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { ...this.headers, 'Accept': 'text/event-stream' },
      body: JSON.stringify({
        text,
        session_id: sessionId,
        device_id: deviceId,
        client_msg_id: Date.now().toString(),
      }),
    });

    if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
    if (!res.body) throw new Error('No response body for streaming');

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let fullText = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim() || !line.startsWith('data: ')) continue;
        const chunk = line.substring(6);
        if (chunk === '[DONE]') break;
        if (chunk.startsWith('[ERROR]')) {
          throw new Error(chunk);
        }
        fullText += chunk;
        onPartial(fullText);
      }
    }
    return fullText;
  }
}

export const brainApi = new BrainApi();
