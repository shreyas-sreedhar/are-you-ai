# Architecture

How RUAI is put together, and why it is put together that way.

## The shape of the thing

```
  Chrome extension                      Next.js site
  ├── video-check.js                    ├── /        the case for it
  ├── message-check.js                  ├── /try     live checks
  └── verdict-view.js ──┐         ┌──── └── /dashboard
                        │         │
                        ▼         ▼
              ┌──────────────────────────────┐
              │  FastAPI                     │
              │                              │
              │  POST /api/v1/check/video    │
              │  POST /api/v1/check/message  │
              │  POST /api/v1/check/article  │
              │  GET  /api/v1/activity/*     │
              └──────────────┬───────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             NVIDIA NIM        checks.csv (local)
```

## One domain model

Everything converges on `core/verdict.py`:

```python
class Verdict(BaseModel):
    kind: CheckKind          # video | message | article
    risk: Risk               # safe | caution | danger
    score: float             # 0 = nothing wrong, 1 = certainly not genuine
    headline: str            # the one line shown in the largest type
    summary: str             # one or two plain sentences
    signals: list[Signal]    # the evidence, strongest first
    advice: list[str]        # what to do next
    analysis_note: str | None
    degraded: bool           # answered without the model
```

This is the whole reason the codebase is small. Adding a fourth kind of check
means writing one analyser and one route — not a new response type, a new
storage table, a new dashboard section and a new card component.

## Request path

Taking a message check as the example:

1. **`api/routes.py`** validates the request and calls the analyser. It owns
   HTTP concerns only.
2. **`services/scam_signals.py`** runs a word-bounded pattern scan in
   microseconds. Its output does two jobs: it briefs the model on what a
   keyword scan already noticed, which measurably improves precision, and it
   is the answer if NIM cannot be reached.
3. **`core/prompts.py`** builds the prompt. All three prompts request the same
   JSON envelope: `{score, signals[], note}`.
4. **`services/nim_client.py`** posts it. One pooled `httpx.AsyncClient` for
   the process lifetime, retries with backoff on 429 and transport errors, no
   retry on other 4xx, closed by the FastAPI lifespan handler.
5. **`core/envelope.py`** reads the reply. Models wrap JSON in markdown
   fences, prepend `<think>` blocks and add trailing commentary, so this
   strips wrappers and walks the string for the first balanced `{...}`,
   ignoring braces inside string literals. A greedy regex gets this wrong.
6. **`core/calibration.py`** caps the score at what the evidence supports.
7. **`core/assembler.py`** turns score plus evidence into the finished
   `Verdict`, pulling every sentence from `core/guidance.py`.
8. **`storage/activity_log.py`** records it — but only if it is concerning.

## Two rules that carry most of the weight

### Calibration

Vision models are eager. Asked "is this AI-generated?", they will return 0.8
and then list three observations amounting to "the lighting is nice". The
original build shipped with this problem, and ordinary cooking videos came
back flagged.

```python
if not signals:                       score = min(score, 0.15)
elif any(s.severity is HIGH ...):     score unchanged
elif no medium signals:               score *= 0.4
elif exactly one medium signal:       score *= 0.7
```

The score is never scaled *up*. A model saying "this is fine" while listing
impossibilities is a case for reading the note, not for overriding it.

### Degradation

Different checks degrade differently, on purpose:

| Check | NIM unreachable | Why |
|---|---|---|
| Message | local scan answers, `degraded: true` | A warning now beats a better warning after the money is gone. |
| Video | 503, "cannot check right now" | There is no honest local fallback. Returning "looks real" is the most harmful thing available. |
| Article | 503, same | Judging a claim needs world knowledge. |

## Copy as a module

`core/guidance.py` holds every sentence a user reads, with the rules that
govern them at the top of the file: short sentences, plain words, never blame
the reader, advice is an action, no exclamation marks. Urgency is the
scammer's tool, not ours.

Keeping it in one file means the copy can be reviewed, translated or read
aloud as one body of text — and it lets the test suite assert on the whole
thing at once.

## Storage

One append-only CSV of verdicts, `backend/data/checks.csv`. Not a database,
because there is no server and no second reader; not two files, because the
previous split into `videos.csv` and `messages.csv` is exactly what made a
single timeline impossible.

It is personal data — a list of what someone watched and who messaged them —
so it is git-ignored, never transmitted, and erasable from the UI. Ordinary
messages are never written at all.

## Front ends

The extension and the website render the same `Verdict` from two twin
components: `extension/shared/verdict-view.js` in vanilla DOM, and
`web/components/VerdictCard.tsx` in React. They are deliberately parallel.

Both are built from `brand/tokens.css`. The web app imports it directly. A
Chrome extension can only load files inside its own directory, so
`scripts/sync_brand.py` writes a generated copy into `extension/styles/`, and
`--check` fails if the copy has drifted.

Nothing in the extension passes page text or model output to `innerHTML`.
`RUAI.el()` builds nodes and assigns `textContent`; the only markup written
directly is the first-party icon set.
