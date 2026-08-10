import 'package:flutter/material.dart';

/// Breakpoints for portrait-first, landscape-flex layouts.
class LayoutTier {
  LayoutTier._(this.width);

  final double width;

  bool get isCompact => width < 600;
  bool get isMedium => width >= 600 && width < 840;
  bool get isExpanded => width >= 840;

  /// Side rail: landscape phones (600+) and tablets/desktop (840+).
  bool get showRail => width >= 600;
}

/// Shell: portrait = single column; landscape/wide = rail + main.
class ResponsiveShell extends StatelessWidget {
  const ResponsiveShell({
    super.key,
    required this.title,
    required this.statusLine,
    required this.bridgeLine,
    this.llmHint,
    required this.onReconnect,
    required this.onNewChat,
    this.onSettings,
    required this.child,
    required this.composer,
  });

  final String title;
  final String statusLine;
  final String bridgeLine;
  final String? llmHint;
  final VoidCallback onReconnect;
  final VoidCallback onNewChat;
  final VoidCallback? onSettings;
  final Widget child;
  final Widget composer;

  @override
  Widget build(BuildContext context) {
    return OrientationBuilder(
      builder: (context, orientation) {
        final width = MediaQuery.sizeOf(context).width;
        final tier = LayoutTier._(width);
        final rail = _SideRail(
          onReconnect: onReconnect,
          onNewChat: onNewChat,
          compact: tier.isCompact && orientation == Orientation.portrait,
        );

        final main = Column(
          children: [
            if (!tier.showRail)
              _TopBar(
                title: title,
                onReconnect: onReconnect,
                onNewChat: onNewChat,
                onSettings: onSettings,
              ),
            Expanded(child: child),
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 8),
              child: composer,
            ),
            _Footer(statusLine: statusLine, bridgeLine: bridgeLine, llmHint: llmHint),
          ],
        );

        if (!tier.showRail) {
          return Scaffold(body: SafeArea(child: main));
        }

        return Scaffold(
          body: SafeArea(
            child: Row(
              children: [
                rail,
                VerticalDivider(width: 1, color: Colors.white.withValues(alpha: 0.08)),
                Expanded(child: main),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({
    required this.title,
    required this.onReconnect,
    required this.onNewChat,
    this.onSettings,
  });

  final String title;
  final VoidCallback onReconnect;
  final VoidCallback onNewChat;
  final VoidCallback? onSettings;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.auto_awesome, color: Color(0xFF8B5CF6)),
          const SizedBox(width: 8),
          Expanded(child: Text(title, style: Theme.of(context).textTheme.titleLarge)),
          if (onSettings != null)
            IconButton(tooltip: 'Brain URL', onPressed: onSettings, icon: const Icon(Icons.settings_outlined)),
          TextButton.icon(onPressed: onNewChat, icon: const Icon(Icons.add_comment), label: const Text('New')),
          TextButton.icon(onPressed: onReconnect, icon: const Icon(Icons.refresh), label: const Text('Reconnect')),
        ],
      ),
    );
  }
}

class _SideRail extends StatelessWidget {
  const _SideRail({
    required this.onReconnect,
    required this.onNewChat,
    required this.compact,
  });

  final VoidCallback onReconnect;
  final VoidCallback onNewChat;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final w = compact ? 56.0 : 72.0;
    return SizedBox(
      width: w,
      child: Column(
        children: [
          const SizedBox(height: 12),
          const Icon(Icons.auto_awesome, color: Color(0xFF8B5CF6)),
          const SizedBox(height: 24),
          IconButton(tooltip: 'New chat', onPressed: onNewChat, icon: const Icon(Icons.add_comment)),
          IconButton(tooltip: 'Reconnect', onPressed: onReconnect, icon: const Icon(Icons.refresh)),
          const Spacer(),
        ],
      ),
    );
  }
}

class _Footer extends StatelessWidget {
  const _Footer({
    required this.statusLine,
    required this.bridgeLine,
    this.llmHint,
  });

  final String statusLine;
  final String bridgeLine;
  final String? llmHint;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(color: Colors.grey, shape: BoxShape.circle),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(statusLine, style: Theme.of(context).textTheme.bodySmall)),
              if (bridgeLine.isNotEmpty) Text(bridgeLine, style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
          if (llmHint != null && llmHint!.isNotEmpty)
            Text(llmHint!, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey)),
        ],
      ),
    );
  }
}
