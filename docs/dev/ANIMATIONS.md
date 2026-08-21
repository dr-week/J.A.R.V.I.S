# UI Animation Presets & Micro-Interactions Specification

This document defines the standardized animation presets, motion timing, and micro-interaction behaviors across Jarvis UI surfaces (Web PWA, Windows Flet, Flutter).

---

## Motion Design System Principles

1. **Purposeful & Non-Intrusive**: Animations should convey status (thinking, listening, executing) without delaying critical user actions.
2. **Fluid Physics**: Use cubic-bezier curves over linear transitions to give elements a natural feel.
3. **Low Overhead**: Use CSS hardware-accelerated properties (`transform`, `opacity`) to ensure 60 FPS performance across mobile and desktop.

---

## Standard Animation Presets

### 1. Neural Idle / Thinking Pulse (`pulse-glow`)
- **Usage**: Used on assistant avatar, mic button, or status badges when the agent is actively processing or listening.
- **CSS Specification**:
```css
@keyframes neuralPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 0 12px rgba(99, 102, 241, 0);
    transform: scale(1.03);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
    transform: scale(1);
  }
}

.neural-active {
  animation: neuralPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

### 2. Fluid Staggered Entrance (`slide-fade-in`)
- **Usage**: Used for incoming chat messages, system alerts, and dynamic card list entries.
- **CSS Specification**:
```css
@keyframes slideFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-entrance {
  animation: slideFadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
```

### 3. Surface Morph & Elevate (`card-hover`)
- **Usage**: Used on dynamic interactive buttons, card containers, and tool execution status popups.
- **CSS Specification**:
```css
.card-interactive {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1),
              border-color 0.2s ease;
}

.card-interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.12);
}
```

### 4. Haptic Click Ripple (`ripple-touch`)
- **Usage**: Instant feedback when pressing control buttons or confirming permissions.
- **Behavior**: Expanding circular fill overlay with exponential fade-out over 250ms.

### 5. Skeleton Shimmer Loader (`shimmer-loading`)
- **Usage**: Placeholder states for loading tool cards, message streams, or subagent tasks.
- **CSS Specification**:
```css
@keyframes shimmerWave {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton-shimmer {
  background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
  background-size: 200% 100%;
  animation: shimmerWave 1.8s infinite linear;
}
```

### 6. Aurora Border Halo (`aurora-border`)
- **Usage**: Highlighting active context focus, active subagent drawers, or pending user approval confirmations.
- **CSS Specification**:
```css
@keyframes auroraGlow {
  0%, 100% { border-color: rgba(99, 102, 241, 0.6); box-shadow: 0 0 15px rgba(99, 102, 241, 0.2); }
  50% { border-color: rgba(168, 85, 247, 0.6); box-shadow: 0 0 22px rgba(168, 85, 247, 0.3); }
}

.aurora-active {
  animation: auroraGlow 4s ease-in-out infinite;
}
```

### 7. Background Gradient Mesh Shift (`mesh-shift`)
- **Usage**: Subtle ambient background motion giving life behind frosted glass panels without flat black `#000`.
- **CSS Specification**:
```css
@keyframes meshShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.ambient-mesh-bg {
  background: radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.15), transparent 40%),
              radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.12), transparent 40%),
              #0f0f13;
  background-size: 180% 180%;
  animation: meshShift 15s ease infinite;
}
```

---

## Integration Guidelines by Surface

- **Web (`clients/web`)**: Include keyframes in core theme CSS and expose utility classes `.animate-neural`, `.animate-entrance`, and `.card-interactive`.
- **Flet (`clients/windows`)**: Apply `flet.Animation` with curve `flet.AnimationCurve.DECELERATE` on containers and cards.
- **Flutter (`clients/flutter`)**: Implement via standard `ImplicitlyAnimatedWidget` / `AnimatedContainer` using `Curves.easeOutCubic`.
