import asyncio
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from models.devices import (
    DEVICE_CONFIGS,
    DeviceModel,
    MediaResponse,
    ScreenshotRequest,
)
from services.capture import take_screenshot
from utils.cleanup import schedule_delete

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["capture"])


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@router.post("/screenshot", response_model=MediaResponse)
async def screenshot(req: ScreenshotRequest, request: Request):
    """Capture a screenshot of any URL across 19 device profiles."""
    try:
        file_path, width, height = await take_screenshot(req)
    except Exception as e:
        logger.error("Screenshot failed: %s", e)
        if "at capacity" in str(e):
            return JSONResponse(status_code=503, content={"detail": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

    asyncio.create_task(schedule_delete(str(file_path)))

    return MediaResponse(
        url=f"{_base_url(request)}/images/{file_path.name}",
        filename=file_path.name,
        device=req.device.value,
        device_label=DEVICE_CONFIGS[req.device]["label"],
        width=width,
        height=height,
    )


@router.get("/devices", tags=["info"])
async def list_devices():
    """Return all available device profiles."""
    return {
        key.value: {
            "label": cfg["label"],
            "width": cfg["width"],
            "height": cfg["height"],
            "is_mobile": cfg["is_mobile"],
        }
        for key, cfg in DEVICE_CONFIGS.items()
    }
