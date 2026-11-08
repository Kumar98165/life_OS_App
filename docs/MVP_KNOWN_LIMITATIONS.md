# LifeOS MVP Known Limitations

> **Version**: 1.0.0  
> **Date**: 2026-11-08  
> **Status**: READY WITH KNOWN LIMITATIONS

---

## 1. Build & Distribution

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No native iOS build (IPA) generated | Cannot install on iOS devices | Use EAS Build: `eas build --platform ios` |
| No native Android build (APK/AAB) generated | Cannot install on Android devices | Use EAS Build: `eas build --platform android` |
| No physical device testing performed | Unknown device-specific issues | All logic tested via automated unit/integration tests |
| No App Store / Play Store submission | Not publicly distributed | Post-MVP release task |
| Web export tested only (975 modules, 2.6MB) | Web is verified; native is unverified | Native builds expected to work (no native modules beyond expo-secure-store) |

---

## 2. Notifications

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| `expo-notifications` not installed as npm dependency | Push notifications not functional at runtime | Install: `npx expo install expo-notifications` when deploying to devices |
| No push notification server (APNs/FCM) configured | Device push delivery unavailable | In-app notification center is fully functional |
| Reminder scheduler runs on-demand, not as background job | Reminders only fire when backend processes them | Implement cron-based scheduler (APScheduler or Celery Beat) in production |
| No background notification polling on mobile | App must be foregrounded to see new notifications | Implement push notifications for real-time delivery |

---

## 3. AI System

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Requires local Ollama installation | AI features unavailable without Ollama running | Graceful fallback response returned on failure |
| No retry logic on LLM timeout | Single 60s attempt per request | Increase timeout or add retry with exponential backoff |
| Intent classification is keyword-based | May misclassify complex queries | Works well for MVP; upgrade to LLM-based classification post-MVP |
| Memory extraction best-effort only | Some memories may not be extracted | Extraction failure silently caught; doesn't break chat |
| No streaming responses | Full response returned at once | Acceptable for 3B model; add SSE streaming post-MVP |
| qwen2.5:3b model limitations | Smaller model may produce less accurate responses | Upgrade to larger model (7B/14B) if hardware supports it |

---

## 4. Security

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Rate limiter uses in-memory storage | Not shared across Gunicorn workers | Switch to `redis://` for `RATELIMIT_STORAGE_URI` |
| CORS defaults to `*` in development | Open to cross-origin requests | Set `CORS_ALLOWED_ORIGINS` to specific origins in production |
| No HTTPS configured (app level) | Traffic unencrypted | Deploy behind Nginx with TLS termination |
| No CSRF protection | API-only backend (JWT-authenticated) | Standard for JWT APIs; add if web frontend is served |
| No IP allowlisting for admin endpoints | Admin accessible from any authenticated admin | Consider IP restrictions for admin operations |

---

## 5. Data & Storage

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No automated database backups | Data loss risk in production | Implement backup script (see DATABASE_BACKUP_RESTORE.md) |
| No data export feature for users | Users cannot download their data | Post-MVP: Add GDPR-compliant data export endpoint |
| No file/image upload support | Cannot attach files to tasks or goals | Post-MVP feature |
| Single-currency per transaction | No multi-currency portfolio view | Each transaction stores ISO 4217 code; aggregation is single-currency |

---

## 6. Performance

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No TanStack Query staleTime configured | Unnecessary refetches on screen focus | Set `staleTime: 30000` on read-heavy queries |
| Analytics computed on-demand (no caching) | Slow for large datasets | Add Redis caching for analytics results |
| No pagination cursor support | Offset-based pagination may slow on deep pages | Acceptable for MVP data volumes |
| Bundle size 2.6MB (web) | Slower initial load on slow connections | Code splitting and lazy loading post-MVP |

---

## 7. Missing Features (Planned Post-MVP)

| Feature | Priority | Notes |
|---------|----------|-------|
| Push notification delivery (APNs/FCM) | HIGH | Requires expo-notifications + server config |
| Background task scheduler | HIGH | For reminders and recurring transactions |
| Data export (GDPR) | MEDIUM | User data download endpoint |
| File attachments | MEDIUM | Task/goal file uploads |
| Multi-device sync | MEDIUM | Already supports multiple sessions via JWT |
| Offline mode | MEDIUM | Queue API calls when offline |
| Dark mode | LOW | Design system supports theming |
| Localization (i18n) | LOW | English-only in MVP |
| Social features | LOW | Share goals/habits with friends |
| Calendar integration | LOW | Sync with Google Calendar / Apple Calendar |

---

## 8. Environment Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Tested with 3.12 |
| Node.js | 18+ | Tested with 22.x |
| PostgreSQL | 14+ | Required for JSONB and UUID support |
| Ollama | Latest | Required for AI features |
| Expo SDK | 53 | React Native 0.79 |

---

## 9. Summary

The LifeOS MVP delivers a complete 14-module personal operating system with:
- ✅ Full authentication with JWT rotation
- ✅ Task, planner, goal, and habit management
- ✅ Local AI assistant with memory and prompt versioning
- ✅ Personal finance management
- ✅ In-app notification center
- ✅ Life analytics dashboard
- ✅ 310 automated tests (166 backend + 144 mobile)
- ✅ 0 TypeScript errors
- ✅ Glassmorphism UI design system

**Primary gap**: Native device builds and push notifications are not yet operational and require EAS Build and notification server configuration for production deployment.
