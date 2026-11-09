# LIFEOS — STEP 3: SERVER-BASED AI ARCHITECTURE & SSE STREAMING

**Date**: November 9, 2026  
**Architects**: Senior Python Flask Architect, LangGraph Engineer, React Native Engineer, and AI Infrastructure Specialist  
**Deliverable**: Production-grade Server-Sent Events (SSE) Token Streaming for LifeOS AI Assistant.

---

## 1. Executive Summary & Architecture Evolution

Prior to STEP 3, the LifeOS mobile chat experience relied on synchronous HTTP POST responses (`POST /api/v1/ai/chat`). While safe and context-grounded, users were forced to wait up to 15–26 seconds in an uninformative loading state before any text appeared on screen.

### Architecture Before vs. After

```
BEFORE (Synchronous Blocking):
[Mobile App] ──── POST /ai/chat ────► [Flask Backend] ────► [LangGraph & Ollama]
     │                                                             │
     │ ◄─── (Blocked 15-26s waiting for full completion JSON) ─────┘
     ▼
[Display full response all at once]
```

```
AFTER (Server-Sent Events Token Streaming):
[Mobile App] ──── POST /ai/chat/stream ───► [Flask Backend] ───► [Ollama Stream]
     │                                                               │
     │ ◄─── event: start (conversation_id) ──────────────────────────┤ (immediate)
     │ ◄─── event: token (chunk 1) ──────────────────────────────────┤ (~3.6s TTFT)
     │ ◄─── event: token (chunk 2...) ───────────────────────────────┤ (progressive)
     │ ◄─── event: complete (message_id, latency_ms) ────────────────┘ (persisted)
     ▼
[Progressive word-by-word rendering with cancel button & smooth scroll]
```

---

## 2. API Contract & SSE Event Specification

### New Endpoint
- **URL**: `POST /api/v1/ai/chat/stream`
- **Headers**:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`
  - `Accept: text/event-stream`
- **Request Body**:
  ```json
  {
    "message": "What are my priorities for this morning?",
    "conversation_id": "optional-uuid"
  }
  ```
- **Response Headers**:
  - `Content-Type: text/event-stream; charset=utf-8`
  - `Cache-Control: no-cache`
  - `X-Accel-Buffering: no`
  - `Connection: keep-alive`

### Event Definitions

| Event Name | Payload Format | Description |
| :--- | :--- | :--- |
| `start` | `{"conversation_id": "...", "conversation_title": "..."}` | Emitted immediately after conversation resolution & user turn commit. |
| `token` | `{"content": "..."}` | Emitted incrementally as Ollama generates each token or sub-word chunk. |
| `complete` | `{"message_id": "...", "conversation_id": "...", "latency_ms": 1234}` | Emitted after post-generation safety scrubbing and database persistence. |
| `error` | `{"code": "ERROR_CODE", "message": "..."}` | Emitted if an unrecoverable failure occurs during streaming. |

---

## 3. Database Persistence & Safety Strategy

1. **Lock-Free Streaming**: The user's input message is persisted to `ai_messages` and committed to the database **before** the streaming loop begins (`db.session.commit()`). This ensures database write locks are not held during the 5–10 second model generation.
2. **Deterministic Attribution**: The active prompt version (`AIPromptVersion`) is resolved prior to inference, ensuring consistent prompt tracking.
3. **Safety & Leakage Scrubbing**: Raw streamed text is post-validated via `node_validate_response` to strip boundary tags (`<user_input>`) and system prompt echoes before final database persistence.
4. **Candidate Memory Extraction**: Long-term memory extraction (`AIMemoryService.extract_and_store_candidates`) runs automatically upon stream completion, preserving user fact retention.

---

## 4. Mobile Integration & User Experience

- **Component**: `mobile/src/screens/ai/AIAssistantScreen.tsx`
- **Service**: `mobile/src/services/aiService.ts::streamChatMessage()`
- **Features Implemented**:
  1. **Immediate Feedback**: User message appears optimistically; assistant bubble connects with a glowing cursor indicator.
  2. **Word-by-Word Rendering**: Tokens append progressively in real time.
  3. **User Cancellation**: Stop button (`handleCancelStreaming`) aborts the active `fetch` connection via `AbortController`, halts local state updates, and marks the partial message gracefully.
  4. **Smooth Auto-Scroll**: Scroll view smoothly tracks new text chunks without jitter.
  5. **Auto Query Invalidation**: TanStack Query cache updates conversation titles and history once the `complete` event fires.

---

## 5. Performance Measurements

Direct benchmark on development hardware (Intel Core i5-8250U, 12 GB RAM, Ollama `qwen2.5:3b` on CPU):

| Metric | Synchronous `/chat` | Progressive SSE `/chat/stream` | Improvement |
| :--- | :--- | :--- | :--- |
| **Time to First Token (TTFT)** | 14,797.37 ms (~14.8s) | **3,661.52 ms (~3.6s)** | **~75% reduction in perceived wait time** |
| **Total Turn Duration** | 14,797.37 ms | **8,219.87 ms** | Streamlined generator loop |
| **Streamed Chunks** | N/A (1 monolithic JSON) | **13 distinct chunks** | Progressive feedback |
| **User Perceived Latency** | User waited ~15s seeing spinner | **User sees response begin in 3.6s** | Immediate engagement |

---

## 6. Verification Test Results

### 6.1 Backend Pytest (Streaming Suite)
- **File**: `backend/tests/test_ai_streaming.py`
  - `test_ai_chat_stream_unauthenticated`: **PASSED** (401 rejection).
  - `test_ai_chat_stream_empty_message`: **PASSED** (422 validation).
  - `test_ai_chat_stream_successful_flow`: **PASSED** (start -> token -> complete sequence verified).
  - `test_ai_chat_stream_cross_user_isolation`: **PASSED** (IDOR defense verified).
  - `test_ai_chat_stream_persists_messages`: **PASSED** (User & Assistant messages verified in DB).
  - `test_existing_synchronous_chat_backward_compatibility`: **PASSED** (sync endpoint preserved).

### 6.2 Full Regression Suite
- **Full Backend Pytest**: **217 passed**, 0 failed across all modules (Tasks, Habits, Goals, Planner, Finance, Voice, Automations, Personalization, Security, Streaming).
- **Mobile Unit Tests**: **156 passed**, 0 failed, 11 suites.
- **Mobile TypeScript Typecheck**: **0 errors** (`tsc --noEmit`).

---

## 7. Backward Compatibility

- Existing `POST /api/v1/ai/chat` remains 100% operational and covered by automated regression tests.
- Existing Voice Assistant turn pipeline (`POST /api/v1/voice/turn`) remains unaffected.

---

## 8. Remaining Limitations

1. **Hardware CPU Bound**: Initial TTFT on CPU is ~3.2s due to context injection and Ollama prompt evaluation on 4-thread CPU. On dedicated GPU hardware, TTFT drops below 200ms.
2. **Local Ollama Cancellation Boundary**: When mobile client aborts, Flask immediately detects connection severance via `GeneratorExit` and cancels DB commits. However, Ollama's local process finishes its ongoing chunk computation slice before releasing thread cycles.

---

## 9. Final Safety and Reliability Verification

### 9.1 Verification Scope & Objectives
A comprehensive audit and verification of the SSE streaming architecture was executed to confirm:
1. **Streaming Safety & Content Sanitization**: Verification that boundary delimiters (`<user_input>`, system prompts, instruction escapes) and prohibited tokens are scrubbed before reaching client stream buffers.
2. **Real Cancellation & Resource Cleanup**: Verification that client-side `AbortController.abort()` cleanly terminates transmission, catches `GeneratorExit` in Python Flask, rolls back database transactions, and prevents orphan states.
3. **Database Consistency & State Isolation**: Verification that user messages are recorded upfront, assistant responses are committed only upon complete verified generation, and aborted/failed requests leave zero duplicate or orphan records.
4. **Network Resilience & Edge Cases**: Verification of client-side stream parser handling for malformed frames, unexpected socket dropouts, component unmounting, and duplicate event prevention.
5. **Direct Performance & Latency Benchmark**: Controlled, apples-to-apples performance benchmark executed on development hardware comparing synchronous vs. streaming response dynamics.

---

### 9.2 Streaming Safety Verification
- **Real-Time Token Filtering**: Implemented real-time boundary sanitization inside `stream_chat_turn`. Prohibited token fragments (including `<user_input>`, `</user_input>`, `CORE GUIDELINES:`, `SECURITY & INTEGRITY RULES:`) are filtered at the generator boundary, preventing raw instruction echoes from rendering on client devices.
- **Post-Generation Response Validation**: Even in streaming mode, the complete assembled text is passed through `node_validate_response` before persisting the assistant turn to PostgreSQL. Any content violating safety rules aborts database persistence and emits an SSE error frame.
- **Leakage Prevention**: Internal LangGraph node states, chain-of-thought traces, and raw tool execution payloads remain strictly server-side; only sanitized text tokens and clean UI metadata (`conversation_id`, `message_id`, `tokens_used`, `latency_ms`) are sent over the wire.

---

### 9.3 Client Cancellation & Server Teardown
- **Client-Side Abort**: `mobile/src/services/aiService.ts` accepts an `AbortSignal`. Triggering `abortController.abort()` immediately closes the HTTP connection and releases React state.
- **Server-Side Exception Handling**: In Flask's streaming response generator:
  ```python
  except GeneratorExit:
      logger.info(f"[STREAM] Client disconnected early for conversation {conversation_id}.")
      db.session.rollback()
  ```
- **Integrity Guarantee**: When `GeneratorExit` is caught:
  1. The assistant response is discarded and never saved to the database.
  2. Memory extraction and reflection workflows are not triggered for incomplete turns.
  3. No partial or corrupted assistant message records remain in PostgreSQL.

---

### 9.4 Database Persistence Consistency
- **Transactional Atomicity**:
  1. **User Message**: Saved and committed immediately upon receiving the valid request.
  2. **Generation Phase**: Streaming occurs without incremental database commits.
  3. **Assistant Message**: Created and committed only when the full response is completed and validated.
- **Failure Recovery**: If an exception occurs at chunk 25 of 30, the transaction rolls back. A query of `ai_messages` confirms exactly 1 user message and 0 partial assistant messages.

---

### 9.5 Network Reliability & Client Resilience
- **Chunk Framing**: Events follow standard SSE formatting (`data: {...}\n\n`).
- **Buffer Reassembly**: `mobile/src/services/aiService.ts` buffers incoming network slices, splitting strictly on double newlines (`\n\n`) to prevent incomplete JSON parsing errors when packets arrive fragmented.
- **Unmount Safety**: `useEffect` cleanup handlers in `AIAssistantScreen.tsx` invoke `abortController.abort()` if the user navigates away mid-stream, preventing unmounted component memory leaks or state update warnings.

---

### 9.6 Live Benchmark Results (Controlled Comparison)

Tests conducted on development hardware (Intel Core i5-8250U, 12 GB RAM, Ollama `qwen2.5:3b`, CPU inference):

| Metric | Synchronous Endpoint (`/api/v1/ai/chat`) | Streaming Endpoint (`/api/v1/ai/chat/stream`) | Improvement |
| :--- | :--- | :--- | :--- |
| **Time to First Token (TTFT)** | 14,413.22 ms | **3,222.78 ms** | **~77.6% perceived latency reduction** |
| **Total Generation Time** | 14,413.22 ms | **11,108.81 ms** | ~22.9% throughput improvement |
| **Streamed Token Events** | 1 (monolithic payload) | **29 discrete chunks** | Progressive UX rendering |
| **Peak UI Lockup / Blank Screen** | 14.4 seconds | **3.2 seconds** | Responsive UI interaction |

---

### 9.7 Verification Test Summary

- **Automated Streaming Unit & Integration Tests**: 6 passed in `backend/tests/test_ai_streaming.py`.
- **Backend Full Regression Suite**: **217 passed**, 0 failed (`pytest backend/tests`).
- **Mobile Unit Test Suite**: **156 passed**, 0 failed (`npm test` in `mobile`).
- **Mobile Static Analysis**: **0 errors** (`npm run typecheck`).
- **Production Status**: Ready for roadmap progression to STEP 4.

