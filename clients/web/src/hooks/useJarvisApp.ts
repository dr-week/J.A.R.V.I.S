import { useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { brainApi } from '../api/brainApi';
import type { SessionInfo } from '../api/brainApi';
import { SyncSocket } from '../api/syncSocket';
import type { ChatMessage, VelocityUpdate, ConfirmRequest } from '../types/chat';

function connectionHint(message: string): string {
  if (message === 'Failed to fetch' || message.includes('NetworkError')) {
    return 'Start the brain from repo root: python scripts/run_brain.py (or .\\scripts\\demo_up.ps1 on Windows)';
  }
  return message;
}

export function useJarvisApp() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isBusy, setIsBusy] = useState(false);
  const [statusLine, setStatusLine] = useState('Starting...');
  const [llmReady, setLlmReady] = useState<boolean | null>(null);
  const [bridgeStatus, setBridgeStatus] = useState('');
  const [activeTab, setActiveTab] = useState<'chat' | 'settings'>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [velocityUpdate, setVelocityUpdate] = useState<VelocityUpdate | null>(null);
  const [confirmRequest, setConfirmRequest] = useState<ConfirmRequest | null>(null);

  const [deviceId] = useState(() => {
    let id = localStorage.getItem('jarvis_device_id');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('jarvis_device_id', id);
    }
    return id;
  });
  const [sessionId, setSessionId] = useState(() => uuidv4());

  const chatEndRef = useRef<HTMLDivElement>(null);
  const syncSocketRef = useRef<SyncSocket | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    let cancelled = false;

    const init = async () => {
      try {
        setStatusLine('Connecting...');
        let token = localStorage.getItem('jarvis_token');
        if (!token) {
          token = await brainApi.pair(deviceId);
          if (cancelled) return;
          localStorage.setItem('jarvis_token', token);
        } else {
          brainApi.setToken(token);
        }

        const health = await brainApi.health();
        setLlmReady(health.llm_ready);
        setStatusLine(`${health.llm_ready ? 'LLM on' : 'LLM off'} · paired`);

        const welcomeText = health.llm_ready
          ? "You're connected — one brain, this session. Ask a question or tell me what you need done."
          : 'Brain is online. Add GEMINI_API_KEY to .env at the repo root, restart the brain, then reload this page.';
        setMessages([{ id: uuidv4(), role: 'system', text: welcomeText }]);

        const socket = new SyncSocket(brainApi.getBaseUrl(), token, deviceId);
        socket.onStatusChange = (status) => {
          if (!cancelled) setBridgeStatus(status);
        };
        socket.onMessage = (msg) => {
          if (cancelled) return;
          if (msg.type === 'velocity_update') {
            setVelocityUpdate(msg.data);
            if (msg.data?.status === 'complete' || msg.data?.status === 'error') {
              setTimeout(() => setVelocityUpdate(null), 5000);
            }
          } else if (msg.type === 'confirm_request') {
            setConfirmRequest({
              request_id: msg.request_id,
              tool: msg.tool,
              params: msg.params,
            });
          }
        };
        socket.connect();
        syncSocketRef.current = socket;

        try {
          const loadedSessions = await brainApi.listSessions();
          if (!cancelled) setSessions(loadedSessions);
        } catch (e) {
          console.error('Failed to load sessions:', e);
        }
      } catch (e: unknown) {
        if (cancelled) return;
        const raw = e instanceof Error ? e.message : String(e);
        setStatusLine('Offline');
        setMessages([
          {
            id: uuidv4(),
            role: 'system',
            text: `Connection error: ${connectionHint(raw)}`,
          },
        ]);
      }
    };
    init();

    return () => {
      cancelled = true;
      syncSocketRef.current?.disconnect();
    };
  }, [deviceId]);

  const handleSend = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isBusy) return;

    setInput('');
    setIsBusy(true);
    setStatusLine('Thinking...');

    const userMsg: ChatMessage = { id: uuidv4(), role: 'user', text: trimmed };
    const assistantId = uuidv4();
    const assistantMsg: ChatMessage = { id: assistantId, role: 'assistant', text: '' };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);

    try {
      await brainApi.streamChat(trimmed, sessionId, deviceId, (partialText) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, text: partialText } : m)),
        );
      });
      setStatusLine('Ready');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setMessages((prev) =>
        prev.map((m) => (m.id === assistantId ? { ...m, text: `Error: ${msg}` } : m)),
      );
      setStatusLine('Send failed');
    } finally {
      setIsBusy(false);
    }
  }, [deviceId, input, isBusy, sessionId]);

  const handleClearChat = useCallback(() => {
    setSessionId(uuidv4());
    setMessages([{ id: uuidv4(), role: 'system', text: 'New session started.' }]);
  }, []);

  const handleLoadSession = useCallback(async (id: string) => {
    try {
      setStatusLine('Loading session...');
      const data = await brainApi.getSession(id);
      if (data.ok) {
        setSessionId(data.session.id);
        const loadedMsgs: ChatMessage[] = data.messages.map((m: any) => ({
          id: uuidv4(),
          role: m.role as ChatMessage['role'],
          text: m.content,
        }));
        setMessages(loadedMsgs);
        setStatusLine('Ready');
        setActiveTab('chat');
        setSidebarOpen(false);
      }
    } catch (e) {
      console.error('Failed to load session:', e);
      setStatusLine('Failed to load session');
    }
  }, []);

  const handleConfirmResult = useCallback((approved: boolean) => {
    if (confirmRequest && syncSocketRef.current) {
      syncSocketRef.current.sendToolResult(confirmRequest.request_id, {
        approved,
      });
      setConfirmRequest(null);
    }
  }, [confirmRequest]);

  const isConnected = statusLine.includes('paired') || statusLine.includes('Ready');

  return {
    messages,
    input,
    setInput,
    isBusy,
    statusLine,
    llmReady,
    bridgeStatus,
    activeTab,
    setActiveTab,
    sidebarOpen,
    setSidebarOpen,
    sessions,
    sessionId,
    velocityUpdate,
    confirmRequest,
    setConfirmRequest,
    chatEndRef,
    handleSend,
    handleClearChat,
    handleLoadSession,
    handleConfirmResult,
    isConnected,
  };
}
