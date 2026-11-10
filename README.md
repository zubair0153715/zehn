# Zehn — ذہن

**Free brain-training studio.** Five original games — Yaad (digit-sequence memory), Rang (Stroop attention), Tez Hisab (maths speed), Do Peeche (2-back flexibility), Raasta (spatial grid memory) — with adaptive difficulty, an honest Zehn Score (0–100 per skill), a rotating daily workout, Zen no-score practice, and a Gemini AI coach. Everything free, everything unlocked.

An original clean-room build from the daily-app-gap-build series. It fills the gaps in **Lumosity: Brain Training** (Premium ~$11.99/month or $59.99–$89/year, price hidden until you sign in; free tier = 3 preselected games a day; Google Play 4.8/5). Zehn is **not affiliated** with Lumos Labs.

## Why Zehn exists

| | Lumosity Premium | Zehn |
|---|---|---|
| Price | ~$11.99/mo or $59.99–$89/yr, hidden until sign-in | **Free, forever** |
| Games | Free: 3 preselected games/day; full library = Premium | **All 5 games, all levels, any time** |
| Daily workout | 5 games chosen by their algorithm = Premium | **Free — rotates daily, leans into your weakest skill** |
| Zen (no-score) practice | Unlocks after 50 games; unlimited = Premium | **Free from game one** |
| Coaching | Insights describe your past score | **AI tip tells you what to practise next, free** |
| Ads | 3+ Premium ads every time you open the app | **None — nothing to sell** |
| Urdu / Roman-Urdu | No — English only | **Yes — EN + Roman-Urdu + Urdu script** |
| Account / billing | Account required; auto-renews; trial forfeits if you buy | **None — scores stay in your browser** |
| Brain claims | FTC fined Lumos Labs $2M (2016) for unproven claims | **Honest: games train the games themselves** |

Gap report: `../market-gaps/daily/2026-11-10-zehn.md` (in the builder's workspace).

## Features

- **Yaad (Memory)** — digit sequences, 3 digits at level 1 up to 7 at level 5, scored position by position.
- **Rang (Attention)** — Stroop: the word says one colour, the ink is another; pick the INK colour. Congruent/incongruent split reported separately.
- **Tez Hisab (Maths speed)** — arithmetic by level: +/− within 20 (L1) → two-digit × two-digit (L5), exact division only.
- **Do Peeche (Flexibility)** — 2-back letter matching with hits, misses, false alarms and correct rejections.
- **Raasta (Spatial memory)** — 3×3 or 4×4 grid, remember the lit cells; scored by precision/recall/F1.
- **Adaptive difficulty** — level up on ≥80% accuracy (and fast enough), down below 50%, else stay. Levels 1–5 per game.
- **Zehn Score (0–100 per skill)** — 70% accuracy + 30% speed (speed factor 1.0 at or under the target time, falling to 0 at twice the target). Targets: Yaad 8s, Rang 3s, Hisab 6s, Peeche 2.5s, Raasta 10s per round. Published on the page — no black box.
- **Daily workout** — 5 games, order rotates by day of year, weakest skill first.
- **Zen practice** — play any game without the score counting. Free from game one.
- **AI coach (Gemini)** — a daily training tip and a weekly summary from your own scores. Labelled AI-written, validated for length and tone.
- **Urdu-first** — EN + Roman-Urdu + Urdu script for every game name and instruction.
- **No account, no storage server-side** — scores and levels live in your browser (localStorage).

## Honest limits

- Brain games train the games themselves. A 2016 review of brain-training research found performance improves on the trained tasks, with thin evidence for transfer to everyday thinking. **Zehn does NOT raise IQ, prevent dementia, or treat any condition** — and says so, because Lumosity's maker paid $2 million to the FTC for claiming otherwise.
- Games are original designs written for this app. Sequence recall, Stroop, arithmetic, 2-back and grid recall are standard cognitive tasks in the public literature, not any company's property. No Lumosity game names, art, code or assets are used.
- AI tips and summaries need `GEMINI_API_KEY` in the environment; without it everything else works fully and the page says the AI is off.

## Run

```bash
# as a FastAPI route (lives at /zehn in the clinic-demo app)
pip install fastapi uvicorn
uvicorn app.main:app --reload   # from the clinic-demo repo
```

Or mount the router from this package in any FastAPI app:

```python
from fastapi import FastAPI
from zehn.routes import router as zehn_router
app = FastAPI()
app.include_router(zehn_router)
```

## Tests

```bash
python tests/verify.py   # exit 0 = all pass; no network, no key needed
python tests/live_check.py   # live Gemini tip + summary via the registered connector
```
