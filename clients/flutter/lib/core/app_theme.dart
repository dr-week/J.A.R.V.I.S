import 'package:flutter/material.dart';

/// Shared tokens — keep aligned with [docs/DESIGN.md].
abstract final class AppTheme {
  static const accentSeed = Color(0xFF0A84FF);
  static const scaffold = Color(0xFF0F0F13);
  static const userBubble = Color(0xFF0A84FF);
  static const assistantBubble = Color(0xFF1E1E2E);

  static ThemeData dark() {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorSchemeSeed: accentSeed,
      scaffoldBackgroundColor: scaffold,
    );
  }
}
