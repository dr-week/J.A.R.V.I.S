import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/app_theme.dart';
import '../../state/chat_controller.dart';
import '../responsive_shell.dart';

class ChatScreen extends StatelessWidget {
  const ChatScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = context.watch<ChatController>();

    return ResponsiveShell(
      title: c.assistantName,
      statusLine: c.statusLine,
      bridgeLine: c.bridgeLine,
      llmHint: c.llmHint,
      onReconnect: () => c.refreshConnection(pairIfNeeded: true),
      onNewChat: c.newChat,
      onSettings: () => _editBrainUrl(context, c),
      composer: _Composer(
        enabled: c.brainOk && !c.busy,
        onSend: c.send,
      ),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: c.messages.length,
        itemBuilder: (context, i) {
          final m = c.messages[i];
          if (m.role == 'system') {
            return _SystemChip(text: m.text);
          }
          return _Bubble(isUser: m.role == 'user', text: m.text);
        },
      ),
    );
  }

  Future<void> _editBrainUrl(BuildContext context, ChatController c) async {
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
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Save')),
        ],
      ),
    );
    if (ok == true && context.mounted) {
      await c.setBrainUrl(ctrl.text);
    }
  }
}

class _Composer extends StatefulWidget {
  const _Composer({required this.enabled, required this.onSend});

  final bool enabled;
  final Future<void> Function(String text) onSend;

  @override
  State<_Composer> createState() => _ComposerState();
}

class _ComposerState extends State<_Composer> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _controller,
            enabled: widget.enabled,
            decoration: const InputDecoration(
              hintText: 'Message Jarvis…',
              border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(24))),
              contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            ),
            onSubmitted: _submit,
          ),
        ),
        const SizedBox(width: 8),
        FilledButton(
          onPressed: widget.enabled ? () => _submit(_controller.text) : null,
          child: const Icon(Icons.send_rounded),
        ),
      ],
    );
  }

  void _submit(String v) {
    final t = v.trim();
    if (t.isEmpty) return;
    widget.onSend(t);
    _controller.clear();
  }
}

class _SystemChip extends StatelessWidget {
  const _SystemChip({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Center(
        child: Text(
          text,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey),
        ),
      ),
    );
  }
}

class _Bubble extends StatelessWidget {
  const _Bubble({required this.isUser, required this.text});

  final bool isUser;
  final String text;

  @override
  Widget build(BuildContext context) {
    final maxW = MediaQuery.sizeOf(context).width * 0.82;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(maxWidth: maxW.clamp(280, 420)),
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isUser ? AppTheme.userBubble : AppTheme.assistantBubble,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 6),
            bottomRight: Radius.circular(isUser ? 6 : 16),
          ),
          boxShadow: const [
            BoxShadow(
              color: Color(0x26000000),
              blurRadius: 12,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: Text(text.isEmpty ? '…' : text),
      ),
    );
  }
}
