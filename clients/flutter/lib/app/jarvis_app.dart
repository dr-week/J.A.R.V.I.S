import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_theme.dart';
import '../core/token_store.dart';
import '../state/field_controller.dart';
import '../ui/field/field_screen.dart';

/// Boots [TokenStore] then provides [FieldController] to the widget tree.
///
/// The Flutter client is the **Field Body** (presence + device actions), not
/// a chat app. See docs/dev/FLUTTER_FIELD.md.
class JarvisApp extends StatelessWidget {
  const JarvisApp({super.key, required this.store});

  final TokenStore store;

  static Future<Widget> bootstrap() async {
    final store = await TokenStore.open();
    return JarvisApp(store: store);
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) {
        final controller = FieldController(store);
        controller.init();
        return controller;
      },
      child: MaterialApp(
        title: 'Jarvis Field',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.dark(),
        home: const FieldScreen(),
      ),
    );
  }
}
