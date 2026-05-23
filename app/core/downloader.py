import os
from typing import List, Optional, Dict, Any

from app.core import DownloaderConfig, DownloadError, ConfigurationError
from app.services import (
	FFmpegManager,
	YtdlpStrategy,
	NetworkCaptureStrategy,
	DirectLinkStrategy
)
from app.utils import setup_logger


logger = setup_logger(__name__)

class VideoDownloader:
	"""Main video downloader class that orchestrates multiple download strategies.
	
	This class provides a unified interface for downloading videos using
	multiple strategies. It tries each strategy in order until one succeeds.
	
	Attributes:
		config: Downloader configuration settings.
		ffmpeg_manager: Manager for FFmpeg operations.
		strategies: List of download strategies to try in order.
		
	Examples:
		>>> downloader = VideoDownloader()
		>>> success = downloader.download('https://example.com/video')
		>>> if success:
		...	 	print('Video downloaded successfully!')
		
		>>> config = DownloaderConfig()
		>>> config.download_path = 'my_videos'
		>>> downloader = VideoDownloader(config)
		>>> results = downloader.download_multiple(['url1', 'url2', 'url3'])
	"""

	def __init__(self, config: Optional[DownloaderConfig] = None):
		"""Initialize the video downloader.
		
		Args:
			config: Optional configuration. If None, loads from environment.
		"""
		self.config = config or DownloaderConfig.from_env()
		self.ffmpeg_manager = FFmpegManager(self.config)
		self.strategies = self._init_strategies()

		self._validate_config()
		self._log_initialization()

	def _init_strategies(self) -> List:
		"""Initialize download strategies in priority order.
		
		Returns:
			List of download strategy instances.
		"""
		return [
			YtdlpStrategy(self.config, self.ffmpeg_manager),
			NetworkCaptureStrategy(self.config, self.ffmpeg_manager),
			DirectLinkStrategy(self.config, self.ffmpeg_manager),
		]

	def _validate_config(self) -> None:
		"""Validate configuration and create necessary directories.
		
		Raises:
			ConfigurationError: If configuration is invalid.
		"""
		try:
			os.makedirs(self.config.download_path, exist_ok=True)
		except OSError as e:
			raise ConfigurationError(f'Cannot create download directory: {e}')

		if self.config.cookie_file:
			if not os.path.exists(self.config.cookie_file):
				logger.warning(f'Cookie file not found: {self.config.cookie_file}')

	def _log_initialization(self) -> None:
		"""Log initialization details including FFmpeg status."""
		logger.info(f'VideoDownloader initialized (headless={self.config.browser.headless_mode})')

		if self.ffmpeg_manager.available:
			logger.info(f'FFmpeg available at: {self.ffmpeg_manager.location}')
		else:
			logger.info(f'FFmpeg not available - downloading in original format')

	def download(self, url: str) -> bool:
		"""Download a video from the given URL.
		
		Tries each download strategy in order until one succeeds.
		
		Args:
			url: Video URL to download.
			
		Returns:
			bool: True if download succeeded.
			
		Raises:
			DownloadError: If all download strategies fail.
			ValueError: If URL is invalid or empty.
			
		Examples:
			>>> downloader = VideoDownloader()
			>>> try:
			...	 	downloader.download('https://youtube.com/watch?v=123')
			... except DownloadError as e:
			...	 	print(f'Failed: {e}')
		"""
		if not url or not isinstance(url, str):
			logger.error(f'Invalid URL: {url}')
			raise DownloadError(f'Invalid URL provided: {url}')

		logger.info(f'Starting download: {url}')

		for strategy in self.strategies:
			try:
				logger.debug(f'Attempting strategy: {strategy.name}')

				if strategy.execute(url):
					logger.info(f'Download succeeded with strategy: {strategy.name}')

					return True
				else:
					logger.debug(f'Strategy {strategy.name} returned False')

			except Exception as e:
				logger.error(f'Strategy {strategy.name} failed: {e}', exc_info=True)

				continue

		logger.error('All download strategies failed')
		raise DownloadError(f'Failed to download video from: {url}')

	def download_multiple(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
		"""Download multiple videos.
		
		Args:
			urls: List of video URLs to download.
			
		Returns:
			dict: Dictionary mapping URLs to download results.
			
		Examples:
			>>> downloader = VideoDownloader()
			>>> results = downloader.download_multiple([
			...	 	'https://example.com/video1',
			...	 	'https://example.com/video2'
			... ])
			>>> for url, result in results.items():
			...	 	print(f"{url}: {'Success' if result['success'] else result['error']}")
		"""
		results = {}

		for url in urls:
			try:
				success = self.download(url)
				results[url] = {
					'success': success,
					'error': None
				}
			except DownloadError as e:
				results[url] = {
					'success': False,
					'error': str(e)
				}
				logger.error(f'Failed to download {url}: {e}')

		return results

	def get_downloads_list(self) -> List[str]:
		"""Get list of downloaded files.

		Returns:
			List of filenames in download directory.
		"""
		try:
			files = os.listdir(self.config.download_path)
			return [f for f in files if os.path.isfile(os.path.join(self.config.download_path, f))]
		except OSError as e:
			logger.error(f'Failed to list downloads: {e}')
			return []
