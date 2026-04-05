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

	def __init__(self, config: DownloaderConfig, ffmpeg_manager: FFmpegManager):
		self.config = config
		self.ffmpeg_manager = ffmpeg_manager
		self._ydl_options = self._build_ydl_options()

	@property
	def name(self) -> str:
		return 'yt-dlp'

	def _build_ydl_options(self) -> dict:
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
		try:
			with yt_dlp.YoutubeDL(self._ydl_options) as ydl:
				ydl.download([url])
				return True
		except Exception as e:
			logger.warning(f'yt-dlp download failed: {e}')
			return False


class NetworkCaptureStrategy(DownloadStrategy):

	def __init__(self, config: DownloaderConfig, ffmpeg_manager: FFmpegManager):
		self.config = config
		self.ffmpeg_manager = ffmpeg_manager
		self.browser_service = BrowserService(config)

	@property
	def name(self):
		return 'network_capture'

	def execute(self, url: str) -> bool:
		video_urls = self.browser_service.capture_network_videos(url)

		if not video_urls:
			logger.debug('No video URLs found in network logs')
			return False

		logger.info(f'Found {len(video_urls)} video URLs')

		return self._download_video_via_url(video_urls[0])

	def _download_video_via_url(self, video_url: str) -> bool:
		ytdlp_strategy = YtdlpStrategy(self.config, self.ffmpeg_manager)
		return ytdlp_strategy.execute(video_url)


class DirectLinkStrategy(DownloadStrategy):

	def __init__(self, config: DownloaderConfig, ffmpeg_manager: FFmpegManager):
		self.config = config
		self.ffmpeg_manager = ffmpeg_manager
		self.browser_service = BrowserService(config)

	@property
	def name(self) -> str:
		return 'direct_link'

	def execute(self, url: str) -> bool:
		video_urls = self.browser_service.find_direct_video_urls(url)

		if not video_urls:
			logger.debug('No direct video links found')
			return False

		logger.info(f'Found {len(video_urls)} direct video links')

		ytdlp_strategy = YtdlpStrategy(self.config, self.ffmpeg_manager)
		return ytdlp_strategy.execute(video_urls[0])	
