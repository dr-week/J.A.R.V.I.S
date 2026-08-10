import 'package:flutter/foundation.dart';
import 'package:logging/logging.dart';
import 'package:uuid/uuid.dart';

import '../core/brain_config.dart';
import '../core/token_store.dart';
import '../data/brain_api.dart';
import '../data/bridge_client.dart';
import '../data/models.dart';

/// L3 — session, messages, connect / pair / send.
class ChatController extends ChangeNotifier {
  ChatController(this._store, {Logger? logger})
      : _log = logger ?? Logger('jarvis.chat');

  final TokenStore _store;
  final Logger _log;
  final _uuid = const Uuid();

  String _sessionId = const Uuid().v4();
  String? _token;
  late String _deviceId;
  late BrainConfig _config;
  BridgeClient? _bridge;

  List<ChatMessage> messages = [];
  bool busy = false;
  bool brainOk = false;
  String statusLine = 'Starting…';
  String bridgeLine = '';

  String assistantName = 'Jarvis';
  bool llmReady = false;
  String? llmHint;

  BrainApi get api => BrainApi(_config, token: _token);

  String get brainUrl => _config.brainUrl;

  Future<void> init() async {
    _deviceId = _store.getOrCreateDeviceId();
    _token = _store.token;
    _config = BrainConfig(
      brainUrl: _store.brainUrl,
      deviceId: _deviceId,
    );
    messages = [
      ChatMessage(
        id: _uuid.v4(),
        role: 'system',
        text: 'Portrait-first UI. Connect to brain to chat.',
      ),
    ];
    await refreshConnection(pairIfNeeded: _token == null);
  }

  Future<void> setBrainUrl(String url) async {
    await _store.setBrainUrl(url);
    _config = BrainConfig(brainUrl: url, deviceId: _deviceId);
    await refreshConnection(pairIfNeeded: true);
  }

  Future<void> refreshConnection({bool pairIfNeeded = false}) async {
    statusLine = 'Connecting…';
    notifyListeners();
    _bridge?.dispose();
    _bridge = null;

    try {
      if (pairIfNeeded || _token == null) {
        _token = await api.pair(deviceId: _deviceId);
        await _store.setToken(_token);
      }
      final health = await api.health();
      brainOk = true;
      assistantName = health.assistantName;
      llmReady = health.llmReady;
      llmHint = llmReady ? null : 'Add GEMINI_API_KEY to backend .env';
      statusLine = '${llmReady ? 'LLM on' : 'LLM off'} · paired';
      _startBridge();
    } on BrainException catch (e) {
      brainOk = false;
      statusLine = 'Offline';
      _log.warning('Brain error: $e');
      _addSystem(e.message, error: true);
    } catch (e, st) {
      brainOk = false;
      statusLine = 'Brain unreachable — start uvicorn on :8787';
      _log.warning('Brain unreachable', e, st);
      _addSystem('$e', error: true);
    }
    notifyListeners();
  }

  void _startBridge() {
    final tok = _token;
    if (tok == null) {
      bridgeLine = 'Bridge: No token';
      notifyListeners();
      return;
    }

    _bridge = BridgeClient(
      brainBase: _config.brainBase,
      token: tok,
      deviceId: _deviceId,
      logger: _log,
    )..onStatusLine = (line) {
        bridgeLine = line;
        notifyListeners();
      };
    _bridge!.connect();
  }

  void newChat() {
    _sessionId = _uuid.v4();
    messages = [
      ChatMessage(id: _uuid.v4(), role: 'system', text: 'New chat started.'),
    ];
    notifyListeners();
  }

  Future<void> send(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || busy || !brainOk) return;

    busy = true;
    messages = [
      ...messages,
      ChatMessage(id: _uuid.v4(), role: 'user', text: trimmed),
      ChatMessage(id: _uuid.v4(), role: 'assistant', text: ''),
    ];
    statusLine = 'Thinking…';
    notifyListeners();

    final assistantId = messages.last.id;
    try {
      await api.streamChat(
        text: trimmed,
        sessionId: _sessionId,
        deviceId: _deviceId,
        onPartial: (partial) {
          _updateMessage(assistantId, partial);
          notifyListeners();
        },
      );
      statusLine = '${llmReady ? 'LLM on' : 'LLM off'} · paired';
    } on BrainException catch (e) {
      _updateMessage(assistantId, 'Error: $e');
      statusLine = 'Send failed';
    } catch (e) {
      _updateMessage(assistantId, 'Error: $e');
      statusLine = 'Send failed';
    }
    busy = false;
    notifyListeners();
  }

  @override
  void dispose() {
    _bridge?.dispose();
    super.dispose();
  }

  void _updateMessage(String id, String text) {
    messages = [
      for (final m in messages)
        if (m.id == id) m.copyWith(text: text) else m,
    ];
  }

  void _addSystem(String text, {bool error = false}) {
    messages = [
      ...messages,
      ChatMessage(id: _uuid.v4(), role: 'system', text: text),
    ];
  }
}
