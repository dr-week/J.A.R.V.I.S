/// L1 — defaults and keys (no network).
class BrainConfig {
  BrainConfig({
    this.brainUrl = defaultBrainUrl,
    this.pairingSecret = defaultPairingSecret,
    this.deviceId = '',
  });

  static const defaultBrainUrl = 'http://10.0.2.2:8787';
  static const defaultPairingSecret = 'change-me';

  /// Web assistant (Vite dev server for `clients/web`) — "Open full assistant".
  static const defaultWebUrl = 'http://localhost:5173';

  static const prefsBrainUrl = 'brain_url';
  static const prefsWebUrl = 'web_url';
  static const prefsToken = 'device_token';
  static const prefsDeviceId = 'device_id';

  final String brainUrl;
  final String pairingSecret;
  final String deviceId;

  String get brainBase => brainUrl.trim().replaceAll(RegExp(r'/+$'), '');
}
