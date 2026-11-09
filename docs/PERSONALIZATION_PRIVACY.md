# LifeOS Personalization Privacy & Control Standards

## 1. Explicit Consent & Zero Secret Profiling

LifeOS strictly forbids covert behavioral profiling:
- **No Hidden AI Inferences**: The AI Assistant does not infer unconfirmed psychological profiles or personal attributes.
- **Explicit User Control**: Every preference field is fully transparent, editable, and optional.
- **Separate Privacy Gates**: AI memory retention, AI learning consent, and everyday UI preferences operate independently. Turning off personalization does not erase memories, nor does resetting the dashboard layout withdraw user training consent.

---

## 2. Granular Data Destruction

- Users can reset specific domains without destructive platform-wide wiping.
- The reset endpoint (`POST /api/v1/personalization/reset`) accepts targeted scopes (`dashboard`, `routine`, `identity`, `ai_style`, `all`).
- When a user deletes their LifeOS account, all personalization and routine records are deleted via cascading foreign keys (`ondelete="CASCADE"`).

---

## 3. Local-First Processing Guarantee

- Personalization configuration is stored solely within the local PostgreSQL database.
- AI prompt customization runs exclusively through the local Ollama instance (`qwen2.5:3b`).
- Zero preference data or personal profile metadata is transmitted to remote cloud analytics or advertising trackers.
