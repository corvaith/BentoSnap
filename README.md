# BentoSnap - Screenshot API

A **FastAPI + Playwright** web API for capturing screenshots of any website across 19 device profiles.
Captured files are **automatically deleted after 5 minutes**.

## What's new in v3.0.0

- **Removed the `/api/record` endpoint** — screenshots only.
- **Shared persistent browser** — one Chromium instance is launched at startup and reused for every request. Previously each request spawned a fresh browser (~1–2 s overhead each), which made concurrent requests fail.
- **Bounded concurrency** — an asyncio semaphore limits parallel captures (`MAX_CONCURRENT_CAPTURES` in `src/services/capture.py`, default 8). Extra requests queue up; if the queue wait exceeds `CAPTURE_QUEUE_TIMEOUT_S` (60 s) the API returns a clean `503` instead of collapsing.
- **Lightweight contexts** — each request creates a browser context (~10–30 ms) instead of a full browser, with full cookie/storage isolation between requests.
- **Verified under load** — 100 simultaneous requests: 100/100 success, zero errors (see Testing below).

## Installation

```shell
# 1. Enter the project folder
cd BentoSnap

# 2. Create a virtualenv and install Python dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Install Playwright browser
.venv/bin/playwright install chromium

# 4. Start the server
.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Server runs at `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

## Project Structure

```
BentoSnap/
├── src/
│   ├── main.py                  # FastAPI entry point (lifespan: starts/stops shared browser)
│   ├── models/
│   │   └── devices.py           # DeviceModel enum + request/response schemas
│   ├── routers/
│   │   └── capture.py           # Routes: /api/screenshot
│   ├── services/
│   │   └── capture.py           # Shared-browser Playwright logic + concurrency control
│   └── utils/
│       └── cleanup.py           # Auto-delete files after 5 minutes
├── uploads/                     # Temporary storage for captured files (auto-created)
├── loadtest.py                  # Escalating concurrency load test (2 → 60 parallel)
├── bursttest.py                 # 100-request simultaneous burst test
├── requirements.txt
└── README.md
```

---

## Device Profiles (19 presets)

| ID | Label | Resolution | Type |
|----|-------|------------|------|
| `desktop_hd` | Desktop HD | 1280×720 | Desktop |
| `desktop_fhd` | Desktop Full HD | 1920×1080 | Desktop |
| `desktop_4k` | Desktop 4K | 3840×2160 | Desktop |
| `desktop_wide` | Ultrawide | 2560×1080 | Desktop |
| `laptop_13` | Laptop 13" | 1280×800 | Laptop |
| `laptop_15` | Laptop 15" | 1440×900 | Laptop |
| `macbook_air` | MacBook Air | 1440×900 | Laptop |
| `macbook_pro` | MacBook Pro 16" | 1728×1117 | Laptop |
| `ipad` | iPad | 820×1180 | Tablet |
| `ipad_pro` | iPad Pro 12.9" | 1024×1366 | Tablet |
| `ipad_mini` | iPad Mini | 768×1024 | Tablet |
| `samsung_tab` | Samsung Galaxy Tab S9 | 800×1280 | Tablet |
| `iphone_se` | iPhone SE | 375×667 | Phone |
| `iphone_14` | iPhone 14 | 390×844 | Phone |
| `iphone_14_pro` | iPhone 14 Pro | 393×852 | Phone |
| `iphone_15_pro` | iPhone 15 Pro | 393×852 | Phone |
| `samsung_s24` | Samsung Galaxy S24 | 384×832 | Phone |
| `pixel_8` | Google Pixel 8 | 412×915 | Phone |
| `xiaomi_14` | Xiaomi 14 | 393×851 | Phone |

---

## Endpoints

### `POST /api/screenshot`

Capture a screenshot of a URL.

**Request body:**
```json
{
  "url": "https://example.com",
  "device": "iphone_14_pro",
  "full_page": true,
  "format": "png",
  "quality": null,
  "wait_ms": 1000,
  "dark_mode": false
}
```

**Response:**
```json
{
  "url": "https://example.com/images/abc123xyz.png",
  "filename": "abc123xyz.png",
  "type": "screenshot",
  "device": "iphone_14_pro",
  "device_label": "iPhone 14 Pro (393×852)",
  "width": 393,
  "height": 852,
  "expires_in_seconds": 300,
  "message": "File will be deleted after 5 minutes."
}
```

---

### `GET /api/devices`

Return a list of all available device profiles.

---

### `GET /images/{filename}`

Serve a captured file directly (PNG / JPEG).
⚠️ Files **expire and are automatically deleted after 5 minutes**.

---

## cURL Examples

```bash
# Desktop screenshot
curl -X POST http://localhost:8000/api/screenshot \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com","device":"desktop_fhd"}'

# iPhone screenshot with dark mode
curl -X POST http://localhost:8000/api/screenshot \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com","device":"iphone_15_pro","dark_mode":true}'
```

---

## Testing

Two test scripts are included (run the server first):

```shell
.venv/bin/python loadtest.py    # 2 → 5 → 10 → 20 → 40 → 60 parallel requests
.venv/bin/python bursttest.py   # 100 simultaneous requests + memory check
```

Results on a 4-core VPS (2026-09-30):

| Concurrency | Success | Avg latency | Max latency |
|-------------|---------|-------------|-------------|
| 2           | 100%    | 2.5 s       | 3.4 s       |
| 5           | 100%    | 4.8 s       | 9.6 s       |
| 10          | 100%    | 7.5 s       | 18.8 s      |
| 20          | 100%    | 9.2 s       | 22.4 s      |
| 40          | 100%    | 11.0 s      | 32.7 s      |
| 60          | 100%    | 10.9 s      | 28.7 s      |
| **100 (burst)** | **100%** | 10.9 s | 34.0 s |

Zero failures at every level.

---

## Scaling to thousands of requests

The concurrency ceiling per instance is CPU/RAM bound. To scale beyond a single box:

1. **Run multiple uvicorn workers** (each gets its own browser):
   ```bash
   pip install gunicorn
   gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```
2. **Run multiple instances behind a load balancer** (nginx / Caddy / cloud LB).
3. **Queue-based architecture** for extreme volume: put requests in Redis/RabbitMQ, run capture workers, return results via webhook or polling.
4. Add **rate limiting + API keys** before exposing publicly — an open screenshot API will be abused.

If running behind a reverse proxy, run uvicorn with `--proxy-headers --forwarded-allow-ips="*"` so file URLs in responses point to the correct public address.
