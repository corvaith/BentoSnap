import asyncio
import logging
import secrets
from pathlib import Path

from playwright.async_api import Browser, async_playwright

from models.devices import (
    DEVICE_CONFIGS,
    ScreenshotRequest,
)

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent
IMAGES_DIR = ROOT_DIR / "uploads" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# --- Concurrency controls ---------------------------------------------------
# How many pages may be captured at the same time inside the shared browser.
# Tune to your CPU/RAM: ~2-3 pages per core is a safe starting point.
MAX_CONCURRENT_CAPTURES = 8
# Requests beyond the semaphore limit wait in this queue; after this long they
# get a clean 503 instead of piling up forever.
CAPTURE_QUEUE_TIMEOUT_S = 60

_browser: Browser | None = None
_playwright = None
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CAPTURES)


async def startup() -> None:
    """Launch one persistent Chromium shared by every request."""
    global _browser, _playwright
    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch(
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
        ]
    )
    logger.info("Shared Chromium browser started")


async def shutdown() -> None:
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
    logger.info("Shared Chromium browser stopped")


def _random_name(ext: str) -> str:
    return secrets.token_urlsafe(12) + "." + ext


async def take_screenshot(req: ScreenshotRequest) -> tuple[Path, int, int]:
    """Capture a screenshot using a lightweight context on the shared browser.

    A new context per request costs ~10-30 ms (vs ~1-2 s for a fresh browser)
    and keeps cookies/storage fully isolated between users.
    """
    if _browser is None:
        raise RuntimeError("Browser not started — call startup() first")

    cfg = DEVICE_CONFIGS[req.device]

    try:
        await asyncio.wait_for(_semaphore.acquire(), timeout=CAPTURE_QUEUE_TIMEOUT_S)
    except asyncio.TimeoutError:
        raise RuntimeError(
            "Server is at capacity, please retry in a moment"
        )

    try:
        filename = _random_name(req.format)
        out_path = IMAGES_DIR / filename

        context = await _browser.new_context(
            viewport={"width": cfg["width"], "height": cfg["height"]},
            device_scale_factor=cfg["device_scale_factor"],
            is_mobile=cfg["is_mobile"],
            user_agent=cfg["user_agent"],
            color_scheme="dark" if req.dark_mode else "light",
        )
        try:
            page = await context.new_page()
            await page.goto(req.url, wait_until="domcontentloaded", timeout=30_000)
            try:
                await page.wait_for_load_state("networkidle", timeout=10_000)
            except Exception:
                pass  # networkidle is best-effort; page is usable without it

            if req.wait_ms:
                await asyncio.sleep(min(req.wait_ms, 10_000) / 1000)

            shot_opts: dict = {"path": str(out_path), "full_page": req.full_page}
            if req.format == "jpeg":
                shot_opts["type"] = "jpeg"
                if req.quality:
                    shot_opts["quality"] = req.quality

            await page.screenshot(**shot_opts)
        finally:
            await context.close()  # frees the page + memory immediately

        return out_path, cfg["width"], cfg["height"]
    finally:
        _semaphore.release()
