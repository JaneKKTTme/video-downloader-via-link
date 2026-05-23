from app.core import VideoDownloader, DownloaderConfig


def get_downloader() -> VideoDownloader:
	config = DownloaderConfig.from_env()
	return VideoDownloader(config=config)