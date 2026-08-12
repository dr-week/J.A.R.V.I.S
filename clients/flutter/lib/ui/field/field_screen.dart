import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/app_theme.dart';
import '../../data/models.dart';
import '../../state/field_controller.dart';

/// L4 — Field Body home screen (presence + device actions, not a chat thread).
///
/// Layout per docs/dev/FLUTTER_FIELD.md:
///   Field · ● Online
///   Pending confirmations
///   Recent device actions
///   [ Open full assistant ] → web
///   ⚙ Brain URL · Device ID
class FieldScreen extends StatelessWidget {
  const FieldScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = context.watch<FieldController>();

    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _StatusHeader(controller: c),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _PendingCard(pending: c.pending),
                  const SizedBox(height: 16),
                  _RecentActionsCard(actions: c.actions),
                ],
              ),
            ),
            _OpenAssistantButton(controller: c),
            _Footer(controller: c),
          ],
        ),
      ),
    );
  }
}

class _StatusHeader extends StatelessWidget {
  const _StatusHeader({required this.controller});

  final FieldController controller;

  @override
  Widget build(BuildContext context) {
    final online = controller.brainOk;
    return Container(
      color: AppTheme.scaffold,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: online ? const Color(0xFF34D399) : Colors.grey,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Field · ${online ? '● Online' : '○ Offline'}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(
                  controller.bridgeLine.isNotEmpty
                      ? controller.bridgeLine
                      : controller.statusLine,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                ),
              ],
            ),
          ),
          IconButton(
            tooltip: 'Reconnect',
            onPressed: () => controller.refreshConnection(pairIfNeeded: true),
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            tooltip: 'Brain URL',
            onPressed: () => _editBrainUrl(context, controller),
            icon: const Icon(Icons.settings_outlined),
          ),
        ],
      ),
    );
  }
}

class _PendingCard extends StatelessWidget {
  const _PendingCard({required this.pending});

  final List<ConfirmRequest> pending;

  @override
  Widget build(BuildContext context) {
    final c = context.read<FieldController>();
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0x19FFFFFF), // ~10% white
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0x1AFFFFFF)),
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Pending confirmations',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      )),
              const SizedBox(height: 12),
              if (pending.isEmpty)
                Text(
                  'No pending tasks. Brain is active.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey),
                )
              else
                for (final p in pending)
                  Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    decoration: BoxDecoration(
                      color: const Color(0x26000000),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ListTile(
                      title: Text(p.tool, style: const TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: Text('${p.params}', style: const TextStyle(fontSize: 12)),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          FilledButton.tonal(
                            onPressed: () => c.denyTool(p),
                            style: FilledButton.styleFrom(backgroundColor: const Color(0x33FF3B30), foregroundColor: const Color(0xFFFF3B30)),
                            child: const Text('Deny')
                          ),
                          const SizedBox(width: 8),
                          FilledButton(
                            onPressed: () => c.approveTool(p),
                            child: const Text('Approve')
                          ),
                        ],
                      ),
                    ),
                  ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecentActionsCard extends StatelessWidget {
  const _RecentActionsCard({required this.actions});

  final List<DeviceAction> actions;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0x19FFFFFF), // ~10% white
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0x1AFFFFFF)),
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Recent device actions',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      )),
              const SizedBox(height: 12),
              if (actions.isEmpty)
                Text(
                  'No actions yet',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey),
                )
              else
                for (final a in actions.take(8))
                  Container(
                    margin: const EdgeInsets.only(bottom: 6),
                    decoration: BoxDecoration(
                      color: const Color(0x26000000),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ListTile(
                      dense: true,
                      leading: Icon(
                        a.status == 'ok' ? Icons.check_circle : Icons.error,
                        color: a.status == 'ok' ? const Color(0xFF34D399) : const Color(0xFFF87171),
                      ),
                      title: Text(a.tool, style: const TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: Text(a.summary, maxLines: 1, overflow: TextOverflow.ellipsis),
                      trailing: Text(
                        _timeAgo(a.at),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ),
                  ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OpenAssistantButton extends StatelessWidget {
  const _OpenAssistantButton({required this.controller});

  final FieldController controller;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      child: FilledButton.icon(
        onPressed: () => _openWeb(controller.webUrl),
        icon: const Icon(Icons.open_in_browser),
        label: const Text('Open full assistant'),
      ),
    );
  }

  Future<void> _openWeb(String url) async {
    final uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      // Failures are visible, not swallowed.
      debugPrint('Could not open web assistant at $url');
    }
  }
}

class _Footer extends StatelessWidget {
  const _Footer({required this.controller});

  final FieldController controller;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 12),
      child: Row(
        children: [
          const Icon(Icons.settings, size: 14, color: Colors.grey),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              'Brain URL · ${controller.brainUrl}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Text(
            'Device ID · ${controller.deviceId}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey,
                ),
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

String _timeAgo(DateTime at) {
  final diff = DateTime.now().difference(at);
  if (diff.inSeconds < 60) return '${diff.inSeconds}s';
  if (diff.inMinutes < 60) return '${diff.inMinutes}m';
  return '${diff.inHours}h';
}

Future<void> _editBrainUrl(BuildContext context, FieldController c) async {
  final ctrl = TextEditingController(text: c.brainUrl);
  final ok = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Brain URL'),
      content: TextField(
        controller: ctrl,
        decoration: const InputDecoration(hintText: 'http://10.0.2.2:8787'),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel')),
        FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Save')),
      ],
    ),
  );
  if (ok == true && context.mounted) {
    await c.setBrainUrl(ctrl.text);
  }
}
