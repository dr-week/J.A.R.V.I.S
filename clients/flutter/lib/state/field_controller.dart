import 'package:flutter/foundation.dart';
import 'package:logging/logging.dart';

import '../core/brain_config.dart';
import '../core/token_store.dart';
import '../data/brain_api.dart';
import '../data/bridge_client.dart';
import '../data/field_bridge_executor.dart';
import '../data/models.dart';

/// L3 — Field Body state: bridge status, tool execution, web link-out.
///
/// Replaces the legacy [ChatController] as the app's default controller.
/// This is presence + device actions, **not** a chat thread.
class FieldController extends ChangeNotifier {
  FieldController(this._store, {Logger? logger})
      : _log = logger ?? Logger('jarvis.field');

  final TokenStore _store;
  final Logger _log;
  final FieldBridgeExecutor _executor = FieldBridgeExecutor();

  String? _token;
  late String _deviceId;
  late BrainConfig _config;
  BridgeClient? _bridge;

  bool paired = false;
  bool brainOk = false;
  bool llmReady = false;
  String statusLine = 'Starting…';
  String bridgeLine = '';

  String assistantName = 'Jarvis';
  String? llmHint;

  /// Pending tool executions awaiting confirmation (from ISSUE-104 onward).
  final List<ToolExecution> pending = [];

  /// Recent device actions for the "Recent device actions" glance.
  List<DeviceAction> actions = [];

  BrainApi get api => BrainApi(_config, token: _token);

  String get brainUrl => _config.brainUrl;
  String get deviceId => _deviceId;

  /// Web assistant URL for "Open full assistant" link-out.
  String get webUrl => _store.webUrl;

  /// Whether desktop tool execution is available on this platform.
  bool get desktopCapable =>
      !kIsWeb &&
      (defaultTargetPlatform == TargetPlatform.windows ||
          defaultTargetPlatform == TargetPlatform.macOS ||
          defaultTargetPlatform == TargetPlatform.linux);

  Future<void> init() async {
    _deviceId = _store.getOrCreateDeviceId();
    _token = _store.token;
    _config = BrainConfig(
      brainUrl: _store.brainUrl,
      deviceId: _deviceId,
    );
    await refreshConnection(pairIfNeeded: _token == null);
  }

  Future<void> setBrainUrl(String url) async {
    await _store.setBrainUrl(url);
    _config = BrainConfig(brainUrl: url, deviceId: _deviceId);
    await refreshConnection(pairIfNeeded: true);
  }

  Future<void> setWebUrl(String url) async {
    await _store.setWebUrl(url);
    notifyListeners();
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
        paired = true;
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
    } catch (e, st) {
      brainOk = false;
      statusLine = 'Brain unreachable — start uvicorn on :8787';
      _log.warning('Brain unreachable', e, st);
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
    )
      ..onStatusLine = (line) {
        bridgeLine = line;
        notifyListeners();
      }
      ..onToolExecute = _handleToolExecute;

    _bridge!.connect();
  }

  Future<Map<String, dynamic>> _handleToolExecute(
    ToolExecution execution,
  ) async {
    // Per ISSUE-033 / PLAN_AUDIT: Android bridge is Kotlin, not Flutter.
    // The executor rejects android_open explicitly; we also gate on desktop.
    final result = _executor.execute(execution.tool, execution.params);
    actions = [
      actionFromResult(execution.tool, result),
      ...actions,
    ];
    if (actions.length > 20) actions = actions.sublist(0, 20);
    notifyListeners();
    return result;
  }

  @override
  void dispose() {
    _bridge?.dispose();
    super.dispose();
  }
}
