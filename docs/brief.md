## Mục tiêu

Khởi động dự án SpeechIt. Đọc brief này, lập kế hoạch đầy đủ, tạo toàn bộ issues và điều phối squad thực thi từ đầu đến nghiệm thu.

## Brief dự án

**SpeechIt** là web tool TTS demo minh họa khả năng phối hợp giữa human và AI agents trên Multica.

| | |
|---|---|
| **Stack** | FastAPI (Python 3.11) · React + Vite + TypeScript + Tailwind |
| **TTS Provider** | Gemini API — model `gemini-3.1-flash-tts-preview` |
| **SDK** | `google-genai` Python SDK (`from google import genai`) |
| **Auth** | `GEMINI_API_KEY` env var — không cần service account hay credentials.json |
| **Audio output** | WAV (PCM 24kHz/16-bit mono, raw từ API) → convert sang MP3 bằng ffmpeg nếu cần, hoặc serve thẳng WAV |
| **Giới hạn cứng** | Input tối đa **8192 tokens** (≈ ~6000 ký tự) · Rate limit **10 req/phút/IP** · Không lưu audio trên server |

**User flow duy nhất:** nhập text → nhập style prompt (tùy chọn) → chọn giọng → nhấn Synthesize → nghe inline + tải về.


**Voices ưu tiên demo:** `Kore` · `Puck` · `Aoede` · `Charon` · `Fenrir`


## Nhiệm vụ của leader-agent

Thực hiện theo thứ tự sau:

**Bước 1 — Tài liệu (tự làm)**
- Viết `docs/PRD.md` với đủ 7 sections: Overview, User flow, Functional requirements (≥8 FR testable), Non-functional requirements, Technical constraints, Acceptance criteria (≥10 AC có số liệu cụ thể), Out of scope
- Viết `docs/api-spec.yaml` (OpenAPI 3.0.3) cho 2 endpoints: `GET /voices` và `POST /synthesize`, đủ schemas, error codes, examples

**Bước 2 — Tạo issues và assign squad**
Tạo đủ 14 issues còn lại theo đúng thứ tự ưu tiên và dependency dưới đây, assign cho squad `speechit-team`:

```
[P1 - sequential]
TTS-02  Viết API Spec — OpenAPI 3.0.3                        → docs-phase
TTS-03  Setup FastAPI project skeleton                        → dev-agent
TTS-07  Setup React + Vite + TypeScript + Tailwind            → dev-agent (parallel với TTS-03)

[P2 - sau khi TTS-03 merged]
TTS-04  Tích hợp Google Cloud TTS SDK                        → dev-agent
TTS-05  Implement GET /voices và POST /synthesize             → dev-agent
TTS-06  Error handling, rate limit, input validation          → dev-agent

[P3 - sau khi TTS-07 merged]
TTS-08  Build TextInput và VoiceSelector component            → dev-agent
TTS-09  Build AudioPlayer và nút Download                     → dev-agent
TTS-10  UX polish — loading states, error UI, responsive      → dev-agent

[P4 - sau khi TTS-05 và TTS-09 merged]
TTS-11  Unit test backend — pytest (coverage ≥ 80%)           → qa-agent
TTS-12  Integration test — Playwright E2E                     → qa-agent
TTS-13  Edge case test + UAT checklist                        → qa-agent

[P5 - sau khi tất cả tests pass]
TTS-14  Docker Compose + deploy                               → dev-agent
TTS-15  Nghiệm thu — UAT trên production + sign-off           → leader-agent
```

Mỗi issue phải có: title rõ ràng, description đủ context, acceptance criteria dạng checkbox, và ghi rõ `depends-on` nếu có.

**Bước 3 — Điều phối**
- Monitor tiến độ qua comments
- Review và merge PR của dev-agent
- Unblock khi có conflict giữa spec và implementation
- Sign-off nghiệm thu ở TTS-15 khi toàn bộ UAT checklist pass

## Acceptance criteria

- [ ] `docs/PRD.md` và `docs/api-spec.yaml` tồn tại trong repo, validate không lỗi
- [ ] 14 issues (TTS-02 → TTS-15) đã được tạo trên Multica với đủ description và AC
- [ ] Issues được assign đúng thứ tự dependency — không assign P2 trước P1 merged
- [ ] Comment vào issue này danh sách link tất cả issues đã tạo sau khi hoàn thành Bước 2

## Dependencies

- **Blocked by:** không có — đây là issue khởi động
- **Blocks:** toàn bộ dự án SpeechIt