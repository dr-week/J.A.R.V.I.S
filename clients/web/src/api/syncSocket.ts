export class SyncSocket {
  private ws: WebSocket | null = null;
  private pingTimer: number | null = null;
  private baseUrl: string;
  private token: string;
  private deviceId: string;
  
  public onStatusChange: (status: string) => void = () => {};
  public onMessage: (msg: any) => void = () => {};

  constructor(baseUrl: string, token: string, deviceId: string) {
    if (baseUrl.startsWith('https://')) {
      this.baseUrl = baseUrl.replace('https://', 'wss://');
    } else if (baseUrl.startsWith('http://')) {
      this.baseUrl = baseUrl.replace('http://', 'ws://');
    } else {
      this.baseUrl = baseUrl.replace(/^http/, 'ws');
    }
    this.token = token;
    this.deviceId = deviceId;
  }

  connect() {
    this.disconnect();
    
    // Pass token via query params if standard header isn't supported in browser websockets easily
    // Note: browser WebSocket API doesn't support custom headers.
    // The backend should support ?token=... or similar if needed.
    // Wait, the backend uses JWT. Let's send the token via subprotocols or query param:
    const wsUrl = `${this.baseUrl}/ws?device_id=${this.deviceId}&token=${this.token}`;
    
    // As per typical web implementations, we might just pass token as a query param or auth protocol.
    this.onStatusChange('Connecting...');
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        this.onStatusChange('Connected');
        // Register device
        this.ws?.send(JSON.stringify({ type: 'register', device_id: this.deviceId, token: this.token }));
        
        // Start ping loop
        this.pingTimer = window.setInterval(() => {
          if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 20000);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ping') {
            this.ws?.send(JSON.stringify({ type: 'pong' }));
          } else if (data.type === 'registered') {
            this.onStatusChange('Connected (Registered)');
          }
          this.onMessage(data);
        } catch (e) {
          console.error('Failed to parse WS message:', e);
        }
      };

      this.ws.onclose = () => {
        this.onStatusChange('Disconnected');
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.onStatusChange('Error');
        // onclose will follow
      };
    } catch (e) {
      this.onStatusChange('Error');
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    this.clearPing();
    setTimeout(() => this.connect(), 5000);
  }

  private clearPing() {
    if (this.pingTimer) {
      window.clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  disconnect() {
    this.clearPing();
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.close();
      this.ws = null;
    }
  }

  sendToolResult(requestId: string, payload: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'tool_result',
          request_id: requestId,
          ...payload,
        })
      );
    }
  }
}
