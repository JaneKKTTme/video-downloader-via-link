from app.core.downloader import VideoDownloader
from app.core.config import DownloaderConfig


def get_downloader() -> VideoDownloader:
	config = DownloaderConfig.from_env()
	return VideoDownloader(config=config)