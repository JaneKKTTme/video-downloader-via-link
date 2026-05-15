from fastapi import APIRouter

from app.core.config import DownloaderConfig
from app.core.schemas import HealthResponse
from app.services.ffmpeg_manager import FFmpegManager


router = APIRouter()

@router.get('/health', response_model=HealthResponse)
async def health_check():
	config = DownloaderConfig.from_env()
	ffmpeg_manager = FFmpegManager(config)

	return HealthResponse(
		status='ok',
		version='1.0.0',
		ffmpeg_availability=ffmpeg_manager.available,
		headless_mode=config.browser.headless_mode
	)
