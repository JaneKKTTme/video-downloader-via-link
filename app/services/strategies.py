from typing import Optional

import yt_dlp

from core.config import DownloaderConfig
from core.interfaces import DownloadStrategy, VideoExtractor
from core.exceptions import DownloadError
from services.browser_service import BrowserService
from services.ffmpeg_manager import FFmpegManager
from utils.logger import setup_logger


logger = setup_logger(__name__)


class YtdlpStrategy(DownloadStrategy):
	"""Download strategy using yt-dlp library.
	
	This strategy leverages yt-dlp, a powerful video downloader that supports
	hundreds of websites and formats.
	
	Attributes:
		config: Downloader configuration.
		ffmpeg_manager: Manager for FFmpeg operations.
	"""

	def __init__(self, config: DownloaderConfig, ffmpeg_manager: FFmpegManager):
		"""Initialize yt-dlp download strategy.
		
		Args:
			config: Downloader configuration.
			ffmpeg_manager: FFmpeg manager for video processing.
		"""
		self.config = config
		self.ffmpeg_manager = ffmpeg_manager
		self._ydl_options = self._build_ydl_options()

	@property
	def name(self) -> str:
		"""Get strategy name.
		
		Returns:
			Strategy identifier 'yt-dlp'.
		"""
		return 'yt-dlp'

	def _build_ydl_options(self) -> dict:
		"""Build yt-dlp configuration options.
		
		Returns:
			dict: Dictionary of yt-dlp options including output template,
			retry settings, and FFmpeg configuration.
		"""
		base_options = {
			'outtmpl': f'{self.config.download_path}/%(title)s.%(ext)s',
			'quiet': False,
			'no_warnings': False,
			'live_from_start': True,
			'wait_for_video': self.config.wait_for_video,
			'retries': self.config.ydl_retries,
			'fragment_retries': self.config.fragment_retries,
			'skip_unavailable_fragments': False,
			'external_downloader': 'ffmpeg',
			'external_downloader_args': {
				'ffmpeg': ['-loglevel', 'quiet']
			},
			'hls_use_mpegts': True,
			'cookiefile': self.config.cookie_file,
		}

		return self.ffmpeg_manager.configure_ydl_options(base_options)

	def execute(self, url: str) -> bool:
		"""Execute download using yt-dlp.
		
		Args:
			url: Video URL to download.
			
		Returns:
			bool: True if download succeeded, False otherwise.
		"""
		try:
			with yt_dlp.YoutubeDL(self._ydl_options) as ydl:
				ydl.download([url])
				return True
		except Exception as e:
			logger.warning(f'yt-dlp download failed: {e}')
			return False


class NetworkCaptureStrategy(DownloadStrategy):
	"""Download strategy using network traffic capture.
	
	This strategy loads the page in a browser, captures network requests,
	and extracts video stream URLs for downloading.
	
	Attributes:
		config: Downloader configuration.
		ffmpeg_manager: Manager for FFmpeg operations.
		browser_service: Service for browser automation.
	"""

	def __init__(self, config: DownloaderConfig, ffmpeg_manager: FFmpegManager):
		"""Initialize network capture strategy.
		
		Args:
			config: Downloader configuration.
			ffmpeg_manager: FFmpeg manager for video processing.
		"""
		self.config = config
		self.ffmpeg_manager = ffmpeg_manager
		self.browser_service = BrowserService(config)

	@property
	def name(self):
		"""Get strategy name.
		
		Returns:
			Strategy identifier 'network_capture'.
		"""
		return 'network_capture'

	def execute(self, url: str) -> bool:
		"""Execute download by capturing network video URLs.
		
		Args:
			url: Web page URL containing the video.
			
		Returns:
			bool: True if video was found and downloaded, False otherwise.
		"""
		video_urls = self.browser_service.capture_network_videos(url)

		if not video_urls:
			logger.debug('No video URLs found in network logs')
			return False

		logger.info(f'Found {len(video_urls)} video URLs')

		return self._download_video_via_url(video_urls[0])

	def _download_video_via_url(self, video_url: str) -> bool:
		"""Download video from direct URL using yt-dlp.
		
		Args:
			video_url: Direct video stream URL.
			
		Returns:
			bool: True if download succeeded, False otherwise.
		"""
		ytdlp_strategy = YtdlpStrategy(self.config, self.ffmpeg_manager)
		return ytdlp_strategy.execute(video_url)


class DirectLinkStrategy(DownloadStrategy):
	"""Download strategy using direct video links from page HTML.
	
	This strategy parses the page HTML for direct video URLs in anchor
	tags and source elements.
	
	Attributes:
		config: Downloader configuration.
		ffmpeg_manager: Manager for FFmpeg operations.
		browser_service: Service for browser automation.
	"""

	def __init__(self, config: DownloaderConfig, ffmpeg_manager: FFmpegManager):
		"""Initialize direct link strategy.
		
		Args:
			config: Downloader configuration.
			ffmpeg_manager: FFmpeg manager for video processing.
		"""
		self.config = config
		self.ffmpeg_manager = ffmpeg_manager
		self.browser_service = BrowserService(config)

	@property
	def name(self) -> str:
		"""Get strategy name.
		
		Returns:
			Strategy identifier 'direct_link'.
		"""
		return 'direct_link'

	def execute(self, url: str) -> bool:
		"""Execute download by finding direct video links on the page.
		
		Args:
			url: Web page URL to search for video links.
			
		Returns:
			bool: True if video was found and downloaded, False otherwise.
		"""
		video_urls = self.browser_service.find_direct_video_urls(url)

		if not video_urls:
			logger.debug('No direct video links found')
			return False

		logger.info(f'Found {len(video_urls)} direct video links')

		ytdlp_strategy = YtdlpStrategy(self.config, self.ffmpeg_manager)
		return ytdlp_strategy.execute(video_urls[0])	
