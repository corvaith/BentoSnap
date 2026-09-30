from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from enum import Enum


class DeviceModel(str, Enum):
    # Desktop
    DESKTOP_HD     = "desktop_hd"
    DESKTOP_FHD    = "desktop_fhd"
    DESKTOP_4K     = "desktop_4k"
    DESKTOP_WIDE   = "desktop_wide"
    # Laptop
    LAPTOP_13      = "laptop_13"
    LAPTOP_15      = "laptop_15"
    MACBOOK_AIR    = "macbook_air"
    MACBOOK_PRO    = "macbook_pro"
    # Tablet
    IPAD           = "ipad"
    IPAD_PRO       = "ipad_pro"
    IPAD_MINI      = "ipad_mini"
    SAMSUNG_TAB    = "samsung_tab"
    # Phone
    IPHONE_SE      = "iphone_se"
    IPHONE_14      = "iphone_14"
    IPHONE_14_PRO  = "iphone_14_pro"
    IPHONE_15_PRO  = "iphone_15_pro"
    SAMSUNG_S24    = "samsung_s24"
    PIXEL_8        = "pixel_8"
    XIAOMI_14      = "xiaomi_14"


DEVICE_CONFIGS: dict[DeviceModel, dict] = {
    DeviceModel.DESKTOP_HD: {
        "label": "Desktop HD (1280×720)",
        "width": 1280, "height": 720,
        "device_scale_factor": 1, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.DESKTOP_FHD: {
        "label": "Desktop Full HD (1920×1080)",
        "width": 1920, "height": 1080,
        "device_scale_factor": 1, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.DESKTOP_4K: {
        "label": "Desktop 4K (3840×2160)",
        "width": 3840, "height": 2160,
        "device_scale_factor": 2, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.DESKTOP_WIDE: {
        "label": "Desktop Ultrawide (2560×1080)",
        "width": 2560, "height": 1080,
        "device_scale_factor": 1, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.LAPTOP_13: {
        "label": "Laptop 13\" (1280×800)",
        "width": 1280, "height": 800,
        "device_scale_factor": 1, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.LAPTOP_15: {
        "label": "Laptop 15\" (1440×900)",
        "width": 1440, "height": 900,
        "device_scale_factor": 1, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.MACBOOK_AIR: {
        "label": "MacBook Air (1440×900)",
        "width": 1440, "height": 900,
        "device_scale_factor": 2, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.MACBOOK_PRO: {
        "label": "MacBook Pro 16\" (1728×1117)",
        "width": 1728, "height": 1117,
        "device_scale_factor": 2, "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    },
    DeviceModel.IPAD: {
        "label": "iPad (820×1180)",
        "width": 820, "height": 1180,
        "device_scale_factor": 2, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    },
    DeviceModel.IPAD_PRO: {
        "label": "iPad Pro 12.9\" (1024×1366)",
        "width": 1024, "height": 1366,
        "device_scale_factor": 2, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    },
    DeviceModel.IPAD_MINI: {
        "label": "iPad Mini (768×1024)",
        "width": 768, "height": 1024,
        "device_scale_factor": 2, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    },
    DeviceModel.SAMSUNG_TAB: {
        "label": "Samsung Galaxy Tab S9 (800×1280)",
        "width": 800, "height": 1280,
        "device_scale_factor": 2, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36",
    },
    DeviceModel.IPHONE_SE: {
        "label": "iPhone SE (375×667)",
        "width": 375, "height": 667,
        "device_scale_factor": 2, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    },
    DeviceModel.IPHONE_14: {
        "label": "iPhone 14 (390×844)",
        "width": 390, "height": 844,
        "device_scale_factor": 3, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    },
    DeviceModel.IPHONE_14_PRO: {
        "label": "iPhone 14 Pro (393×852)",
        "width": 393, "height": 852,
        "device_scale_factor": 3, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    },
    DeviceModel.IPHONE_15_PRO: {
        "label": "iPhone 15 Pro (393×852)",
        "width": 393, "height": 852,
        "device_scale_factor": 3, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    },
    DeviceModel.SAMSUNG_S24: {
        "label": "Samsung Galaxy S24 (384×832)",
        "width": 384, "height": 832,
        "device_scale_factor": 3, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36",
    },
    DeviceModel.PIXEL_8: {
        "label": "Google Pixel 8 (412×915)",
        "width": 412, "height": 915,
        "device_scale_factor": 2, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36",
    },
    DeviceModel.XIAOMI_14: {
        "label": "Xiaomi 14 (393×851)",
        "width": 393, "height": 851,
        "device_scale_factor": 3, "is_mobile": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 14; 2403PN0DC) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36",
    },
}


class ScreenshotRequest(BaseModel):
    url: str
    device: DeviceModel = DeviceModel.DESKTOP_FHD
    full_page: bool = True
    format: Literal["png", "jpeg"] = "png"
    quality: Optional[int] = None          # jpeg only, 1-100
    wait_ms: int = 1000                    # extra wait after load (ms)
    dark_mode: bool = False

    @field_validator("url")
    @classmethod
    def add_scheme(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            v = "https://" + v
        return v

    @field_validator("wait_ms")
    @classmethod
    def cap_wait(cls, v: int) -> int:
        return max(0, min(v, 10_000))

    @field_validator("quality")
    @classmethod
    def check_quality(cls, v):
        if v is None or v == 0:
            return None  # treat 0 same as unset; irrelevant for PNG
        if not (1 <= v <= 100):
            raise ValueError("quality must be between 1 and 100")
        return v


class MediaResponse(BaseModel):
    url: str
    filename: str
    type: Literal["screenshot"] = "screenshot"
    device: str
    device_label: str
    width: int
    height: int
    expires_in_seconds: int = 300
    message: str = "File will be deleted after 5 minutes."
