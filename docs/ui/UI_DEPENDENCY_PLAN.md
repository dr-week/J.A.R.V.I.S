# Jarvis UI Dependency Plan & Bundle Optimization

> **Core Philosophy:** Zero-bloat, ultra-low bundle size, instant startup time (<500ms), and zero-drift package versions across all client platforms.

---

## 1. Web Client Stack (`clients/web`)

### Minimalist Dependency Matrix
| Package | Version | Purpose | Bundle Impact | Why Chosen Over Alternatives |
|---|---|---|---|---|
| `react` + `react-dom` | `^18.3.1` | Core Reactive UI View Layer | ~42 KB (gzipped) | Battle-tested, zero-drift |
| `vite` | `^5.4.0` | Next-Gen Dev Server & Bundler | 0 KB (Dev only) | Sub-second HMR and instant builds |
| `lucide-react` | `^0.440.0` | Lightweight Tree-Shakeable Icons | ~2 KB per icon | Standardized iconography across all HUD screens |
| `clsx` + `tailwind-merge` | Latest | Dynamic Utility Class Combining | ~1.8 KB | Robust conditional styling for glassmorphism |
| `zustand` | `^4.5.5` | Atomic, Boilerplate-Free State Store | ~1.1 KB | Replaces heavy Redux/MobX, 10x faster state updates |

### Prohibited / Anti-Bloat Dependencies (Banned)
- ❌ **No heavy charting libraries (`echarts`, `d3`)** for basic gauges: Use lightweight SVG sparklines or CSS-based bar indicators.
- ❌ **No Moment.js:** Use native `Intl.DateTimeFormat` or `date-fns` (tree-shaken).
- ❌ **No CSS-in-JS runtimes (`styled-components` / `emotion`):** Zero runtime CSS overhead via Tailwind utility compilation.

---

## 2. Flutter Mobile & Field Body Client Stack (`clients/flutter`)

### Approved Flutter Packages
```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management & Controllers
  flutter_riverpod: ^2.5.1      # Compile-safe, zero-boilerplate reactive state
  
  # Networking & Real-Time Sync
  web_socket_channel: ^3.0.1    # Real-time bidirectional connection to Brain
  http: ^1.2.2                  # Standard REST operations
  
  # UI Primitives & System Integration
  url_launcher: ^6.3.0          # 1-tap open deals, links, and documents
  flutter_svg: ^2.0.10+1        # Sharp vector icon rendering
  google_fonts: ^6.2.1          # Inter typography fallback
```

---

## 3. Dependency Loading & Build Verification Plan

### Step 1: Pre-Build AST Validation (Velocity Rule)
Before writing or compiling frontend code, verify that:
1. No circular imports exist between controllers and UI views.
2. All environment variables (`VITE_BRAIN_WS_URL`, `VITE_API_URL`) use fallback defaults (`ws://localhost:8787`).

### Step 2: Bundle Size Assertion Gate
- Web production bundle (`dist/assets/*.js`) must remain under **250 KB compressed**.
- Cold start on desktop and mobile web must initialize in under **400 ms**.
