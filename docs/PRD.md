# SpeechIt — Product Requirements Document

**Version:** 1.0  
**Date:** 2026-06-20  
**Author:** leader-agent  
**Status:** Approved

---

## 1. Overview

**SpeechIt** is a public web demo that converts text to speech using the Gemini API (`gemini-3.1-flash-tts-preview` model). It showcases human–AI agent collaboration on the Multica platform.

**Problem:** Developers and content creators need a quick, accessible way to preview Gemini's TTS capabilities without writing code.

**Solution:** A single-page web application with a minimal UI: paste text, optionally add a style prompt, select a voice, click Synthesize — then hear and download the audio.

**Stakeholders:** demo users (no account required), project owner, Multica squad.

---

## 2. User Flow

```
[Landing page]
      │
      ▼
[Text area] ─── user types/pastes text (≤ ~6000 chars)
      │
      ▼
[Style prompt field] ─── optional free-text (e.g. "speak slowly with warmth")
      │
      ▼
[Voice selector] ─── dropdown: Kore | Puck | Aoede | Charon | Fenrir
      │
      ▼
[Synthesize button] ─── POST /synthesize
      │
      ├─ [Loading spinner] while waiting for response
      │
      ├─ [Error banner] on failure (rate-limit, validation, API error)
      │
      └─ [Audio player + Download button] on success
             │
             └─ user listens inline or clicks Download to save .wav
```

**Entry point:** `GET /` (React SPA)  
**Backend call:** `POST /api/synthesize`  
**Voice list:** `GET /api/voices`

---

## 3. Functional Requirements

| ID    | Requirement | Test Case |
|-------|-------------|-----------|
| FR-01 | The app MUST display a text input area accepting up to 8192 tokens (≈ 6000 characters). | Submit text of exactly 6000 chars → synthesis proceeds. Submit 6001 chars → 422 error returned. |
| FR-02 | The app MUST provide an optional style prompt field (free text, max 500 chars). | Submit with empty style prompt → synthesis proceeds. Submit with non-empty → included in TTS request. |
| FR-03 | The app MUST display a voice selector populated from `GET /api/voices`. | On load, selector shows exactly 5 voices: Kore, Puck, Aoede, Charon, Fenrir. |
| FR-04 | The app MUST call `POST /api/synthesize` when the user clicks Synthesize. | Network tab shows POST to `/api/synthesize` with `{text, voice, style_prompt}` body. |
| FR-05 | The backend MUST call the Gemini API using `google-genai` SDK with model `gemini-3.1-flash-tts-preview`. | Mock Gemini SDK; assert model name passed equals `gemini-3.1-flash-tts-preview`. |
| FR-06 | The backend MUST stream audio bytes directly to the client — no file written to disk. | File system has no audio files after 100 synthesis requests. |
| FR-07 | The frontend MUST display an inline HTML5 `<audio>` player with the synthesized audio when synthesis succeeds. | After successful synthesis, `<audio>` element is visible and `src` is a blob URL. |
| FR-08 | The frontend MUST provide a Download button that saves the audio file as `.wav`. | Clicking Download triggers browser file save dialog with filename ending in `.wav`. |
| FR-09 | The backend MUST enforce a rate limit of 10 requests per minute per IP using slowapi. | 11th request within 60 s from same IP returns HTTP 429 with `{"error": "rate_limit_exceeded"}`. |
| FR-10 | The backend MUST return HTTP 422 with `{"error": "input_too_long"}` when text exceeds limit. | POST with 6001-char text returns 422 `{"error": "input_too_long"}`. |
| FR-11 | The frontend MUST display an error banner with the error message when synthesis fails. | Mock backend to return 429 → red banner "Rate limit exceeded. Try again in 60 s." appears. |
| FR-12 | The backend MUST return the voice list as JSON from `GET /api/voices`. | `GET /api/voices` returns `{"voices": ["Kore","Puck","Aoede","Charon","Fenrir"]}`. |

---

## 4. Non-Functional Requirements

| ID     | Category       | Requirement |
|--------|----------------|-------------|
| NFR-01 | Performance    | `POST /api/synthesize` must return first byte within 10 s under normal load (single user, typical text ≤ 500 chars). |
| NFR-02 | Availability   | Backend must start and serve requests within 30 s of `docker compose up`. |
| NFR-03 | Usability      | UI must be usable on Chrome 120+, Firefox 121+, Safari 17+ without polyfills. |
| NFR-04 | Accessibility  | All interactive elements must have ARIA labels or visible labels. |
| NFR-05 | Security       | `GEMINI_API_KEY` must be read from environment variable only — never hardcoded or logged. |
| NFR-06 | Maintainability| Backend code coverage ≥ 80% as measured by `pytest --cov`. |
| NFR-07 | Portability    | Full stack must run via `docker compose up` on any Linux host with Docker 24+. |

---

## 5. Technical Constraints

| Constraint | Value |
|-----------|-------|
| Backend language | Python 3.11+ |
| Backend framework | FastAPI (latest stable) |
| TTS SDK | `google-genai` (`from google import genai`) |
| TTS model | `gemini-3.1-flash-tts-preview` |
| Auth | `GEMINI_API_KEY` env var only |
| Audio format | WAV (PCM 24 kHz / 16-bit / mono) — served directly, no transcoding required |
| Max input | 8192 tokens (enforced as ≈ 6000 characters by the backend) |
| Rate limit | 10 requests / minute / IP (slowapi, in-memory) |
| Server-side storage | None — audio bytes streamed directly to client |
| Frontend language | TypeScript |
| Frontend framework | React 18 + Vite 5 |
| CSS framework | Tailwind CSS 3 |
| Container | Docker Compose (one service: `backend`; frontend served as static files or separate service) |
| Test framework (backend) | pytest + httpx (async) |
| Test framework (E2E) | Playwright |

---

## 6. Acceptance Criteria

| ID    | Criterion | Measurement |
|-------|-----------|-------------|
| AC-01 | Text input accepts exactly up to 6000 characters. | Submit 6000 chars → HTTP 200. Submit 6001 chars → HTTP 422. |
| AC-02 | Voice selector lists exactly 5 voices on page load. | `GET /api/voices` returns list of length 5. |
| AC-03 | Synthesize button is disabled while a request is in flight. | During loading, button has `disabled` attribute. |
| AC-04 | Audio player appears within 15 s of clicking Synthesize (normal text ≤ 500 chars). | Playwright assertion: `audio` visible within 15 000 ms. |
| AC-05 | Rate limit triggers on 11th request within 60 s from same IP. | Automated test: 11 sequential requests → 11th returns HTTP 429. |
| AC-06 | Error banner is visible and contains actionable text on any API error. | Playwright: mock 500 response → banner with non-empty text appears within 2 s. |
| AC-07 | Download button saves a `.wav` file. | Playwright download fixture: saved file extension is `.wav`, size > 0 bytes. |
| AC-08 | `GEMINI_API_KEY` does not appear in any log line. | Run synthesis; grep server logs for the literal key value → 0 matches. |
| AC-09 | `pytest --cov=app` reports coverage ≥ 80%. | CI output shows `TOTAL ... 80%` or higher. |
| AC-10 | `docker compose up` brings the full stack online within 60 s. | `curl http://localhost:8000/api/voices` returns 200 within 60 s of compose start. |
| AC-11 | No audio files exist in the container filesystem after synthesis. | `docker exec backend find / -name "*.wav" 2>/dev/null` → empty output. |
| AC-12 | Style prompt field is optional — omitting it does not cause an error. | POST without `style_prompt` key → HTTP 200. |

---

## 7. Out of Scope

- **Authentication / user accounts** — this is a public demo with no login.
- **History / library** — no saved synthesis history, no database.
- **Multiple TTS providers** — only Gemini API; no fallback provider.
- **Server-side audio transcoding** — audio is served as WAV; MP3 conversion is not implemented.
- **Streaming audio playback** — audio is fully buffered before playback begins.
- **Mobile-native apps** — web only (responsive design is in scope).
- **Analytics / telemetry** — no tracking, no metrics dashboard.
- **Admin panel** — no management UI.
- **Multi-language UI** — English-only interface.
