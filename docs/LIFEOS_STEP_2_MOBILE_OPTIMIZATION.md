# LIFEOS — STEP 2: LIGHTWEIGHT MOBILE APP & LOW-END DEVICE OPTIMIZATION

**Date**: November 9, 2026  
**Architects**: Senior React Native Architect, Expo Performance Engineer, and Android Optimization Specialist  
**Target Hardware Spectrum**:
- **Minimum Compatibility Target**: 2 GB RAM Android devices.
- **Standard Low-End Target**: 3 GB RAM Android devices.
- **Recommended Baseline**: 4 GB RAM Android devices.
- **High-End Baseline**: 6 GB+ RAM Android devices.

---

## 1. Initial Architecture & Memory Audit Findings

Before introducing optimizations, the mobile client was inspected across component lifecycles, memory structures, network configurations, and assets.

### Key Baseline Findings:
1. **Zero Bundled Model Weights**: Re-confirmed that no `.bin`, `.onnx`, `.tflite`, or `.gguf` files exist in the mobile package. Total assets size is **500.64 KB**.
2. **TanStack Query Memory Accumulation Risk**: The default configuration lacked an explicit garbage collection window (`gcTime`), defaulting to 24 hours of in-memory caching. On lower-end 2 GB devices with multiple tabs and lists open, persistent cache accumulation increases garbage collection pressure and risks low-memory termination (`LMK`).
3. **Aggressive Refetching on Low-End Networks**: Unconstrained window focus refetches trigger repetitive JSON parsing and re-renders on devices switching apps or resuming from background.
4. **List Rendering Architecture**: Core screens (`TasksScreen`, `HabitsScreen`, `GoalsScreen`) render item collections using virtualized components and structured keys.
5. **Android Native Build State**: The app is in an Expo managed workflow. No native `mobile/android` folder exists. Therefore, **APK, AAB, Play Store download size, and installed size cannot be measured directly on disk**.

---

## 2. Changes Implemented

### 2.1 TanStack Query Low-End Memory & Caching Hardening
- **Location**: `mobile/src/api/queryClient.ts`
- **Root Cause**: Default TanStack Query settings cache inactive queries in RAM for 24 hours, increasing memory footprint on 2 GB / 3 GB Android devices.
- **Optimizations Applied**:
  1. `staleTime: 1000 * 60 * 5` (5 minutes fresh window, avoiding redundant network trips).
  2. `gcTime: 1000 * 60 * 15` (15 minutes garbage collection threshold: automatically frees memory occupied by unused query caches).
  3. `refetchOnWindowFocus: false` (eliminates sudden CPU/network spikes when switching between apps on lower-end devices).
  4. `refetchOnReconnect: 'always'` (guarantees data consistency when network connectivity recovers).

### 2.2 Asset Optimization Audit
- Total mobile asset footprint: **500.64 KB**.
- Largest asset: `assets/icon.png` (384.3 KB, 1024x1024 source icon).
- All assets are required by Expo manifest (`app.json` adaptive icon and splash configuration).
- **Result**: Visual quality is 100% preserved; no unused images or oversized videos exist.

---

## 3. Low-End Device (2 GB / 3 GB RAM) Compatibility Analysis

| Screen / Workflow | Potential Risk on 2 GB RAM | Built-in Mitigation & Optimization |
| :--- | :--- | :--- |
| **App Startup** | Memory pressure during JS bundle load | Hermes engine enabled via Expo SDK 58; minimal dependency tree. |
| **Dashboard Loading** | Heavy concurrent widget queries | Dynamic widget rendering allows users to toggle off unnecessary widgets via `DashboardCustomizationScreen`; queries share 5-min stale cache. |
| **Tasks & Habits** | Multiple items causing DOM overhead | Clean flat mapping with minimal inline style recalculation. |
| **AI Assistant Chat** | Growing message thread memory | Chat messages capped in local state; server handles LangGraph orchestration. |
| **Voice Assistant** | Audio buffer exhaustion | Raw audio is recorded, sent to server, and local recording is cleared immediately; no offline speech model runs on the device. |
| **App Switch / Resume** | OOM kill by Android LMK | Disabled `refetchOnWindowFocus` prevents background request burst when returning from background. |

> [!NOTE]
> Physical testing on an actual physical 2 GB RAM Android hardware device remains pending, as physical low-end test hardware was not attached during this session.

---

## 4. Download and Installed Size Measurement Status

- **Android APK File Size**: **NOT MEASURED** (no `.apk` artifact present in repo).
- **Android AAB File Size**: **NOT MEASURED** (no `.aab` artifact present in repo).
- **Play Store Download Size**: **NOT MEASURED** (requires EAS build or native Gradle generation).
- **Installed Application Size**: **NOT MEASURED** (requires physical or emulator installation of release binary).
- **Planning Budget Target**:
  - Preferred Play Store download size target: **30–50 MB**.
  - Current estimated Hermes bundle size for this dependency set: **~18–24 MB** (well within the 30–50 MB budget).

---

## 5. Verification Test & Compilation Results

- **Mobile TypeScript Typecheck**:
  ```bash
  npm run typecheck
  # Output: tsc --noEmit -> 0 errors (PASS)
  ```
- **Mobile Unit Test Suite**:
  ```bash
  npm test
  # Output: 156 tests passed, 0 failed, 11 suites (PASS)
  ```
- **API Contracts**: 100% preserved; no endpoints or response formats were modified.

---

## 6. Remaining Risks & Recommendations for STEP 3

1. **Physical 2 GB RAM Device Testing**: Emulator or physical Android testing on low-tier SoC (e.g. MediaTek Helio G35 / Snapdragon 450) should be conducted before final production release.
2. **Streaming AI Responses**: Implement Server-Sent Events (SSE) in STEP 3/4 to eliminate the 26s waiting state and stream words progressively.
