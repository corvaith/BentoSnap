import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

SRC_DIR = Path(__file__).parent
ROOT_DIR = SRC_DIR.parent

IMAGES_DIR = ROOT_DIR / "uploads" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SRC_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

from services.capture import shutdown, startup  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()      # launch the shared Chromium once
    yield
    await shutdown()     # close it cleanly on exit


app = FastAPI(
    title="BentoSnap — Screenshot API",
    description=(
        "Capture screenshots of any URL across 19 device profiles "
        "(desktop, laptop, tablet, phone).\n\n"
        "Files are **automatically deleted after 5 minutes**.\n\n"
        "Built on a shared persistent browser with bounded concurrency — "
        "designed for high-traffic public use."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

from routers.capture import router as capture_router  # noqa: E402

app.include_router(capture_router)


@app.get("/", tags=["info"])
async def root():
    return {
        "service": "BentoSnap — Screenshot API",
        "version": "3.0.0",
        "endpoints": {
            "POST /api/screenshot": "Capture a screenshot (PNG/JPEG)",
            "GET  /api/devices":    "List all 19 device profiles",
            "GET  /images/{file}":  "Serve screenshot files (expires 5 min)",
            "GET  /docs":           "Interactive API docs (Swagger UI)",
        },
    }
