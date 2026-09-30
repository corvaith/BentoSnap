import asyncio
import os
import logging

logger = logging.getLogger(__name__)


async def schedule_delete(path: str, delay_seconds: int = 300) -> None:
    """Delete *path* after *delay_seconds* seconds (default 5 min)."""
    await asyncio.sleep(delay_seconds)
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Auto-deleted expired file: {path}")
    except Exception as e:
        logger.warning(f"Could not delete {path}: {e}")
