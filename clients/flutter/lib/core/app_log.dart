import 'package:logging/logging.dart';

/// One place to tune log levels for the Flutter client.
final log = Logger('jarvis.flutter');

void configureAppLogging() {
  Logger.root.level = Level.INFO;
  Logger.root.onRecord.listen((record) {
    // ignore: avoid_print
    print('[${record.level.name}] ${record.loggerName}: ${record.message}');
  });
}
