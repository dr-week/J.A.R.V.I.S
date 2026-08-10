import 'package:flutter/material.dart';

import 'app/jarvis_app.dart';
import 'core/app_log.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  configureAppLogging();
  final app = await JarvisApp.bootstrap();
  runApp(app);
}
