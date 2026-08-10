import 'package:shared_preferences/shared_preferences.dart';

import 'brain_config.dart';

/// L1 — persisted brain URL, web URL, token, stable device id.
class TokenStore {
  TokenStore(this._prefs);

  final SharedPreferences _prefs;

  static Future<TokenStore> open() async {
    final prefs = await SharedPreferences.getInstance();
    return TokenStore(prefs);
  }

  String get brainUrl =>
      _prefs.getString(BrainConfig.prefsBrainUrl) ?? BrainConfig.defaultBrainUrl;

  Future<void> setBrainUrl(String url) =>
      _prefs.setString(BrainConfig.prefsBrainUrl, url.trim());

  String get webUrl =>
      _prefs.getString(BrainConfig.prefsWebUrl) ?? BrainConfig.defaultWebUrl;

  Future<void> setWebUrl(String url) =>
      _prefs.setString(BrainConfig.prefsWebUrl, url.trim());

  String? get token => _prefs.getString(BrainConfig.prefsToken);

  Future<void> setToken(String? value) async {
    if (value == null || value.isEmpty) {
      await _prefs.remove(BrainConfig.prefsToken);
    } else {
      await _prefs.setString(BrainConfig.prefsToken, value);
    }
  }

  String getOrCreateDeviceId() {
    final existing = _prefs.getString(BrainConfig.prefsDeviceId);
    if (existing != null && existing.isNotEmpty) return existing;
    final id = 'flutter-${DateTime.now().millisecondsSinceEpoch.toRadixString(16)}';
    _prefs.setString(BrainConfig.prefsDeviceId, id);
    return id;
  }
}
