import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_presence/data/models.dart';

void main() {
  test('HealthInfo parses brain /health JSON', () {
    final h = HealthInfo.fromJson({
      'status': 'ok',
      'assistant_name': 'Jarvis',
      'llm_ready': false,
    });
    expect(h.assistantName, 'Jarvis');
    expect(h.llmReady, false);
  });
}
