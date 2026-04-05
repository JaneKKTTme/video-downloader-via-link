import shutil
import os
from typing import Optional

from core.config import DownloaderConfig
from core.exceptions import FFmpegError
from utils.logger import setup_logger


logger = setup_logger(__name__)


class FFmpegManager:

	def __init__(self, config: DownloaderConfig):
		self.config = config
		self.available = False
		self.location: Optional[str] = None
		self._check_ffmpeg()

	def _check_ffmpeg(self) -> bool:
		if self.config.ffmpeg_location:
			if os.path.exists(self.config.ffmpeg_location):
				logger.info(f'FFmpeg found at: {self.config.ffmpeg_location}')
				self.location = self.config.ffmpeg_location
				self.available = True
				return True
			else:
				logger.warning(f'Configured FFmpeg path not found: {self.config.ffmpeg_location}')

		ffmpeg_path = shutil.which('ffmpeg')
		if ffmpeg_path:
			logger.info(f'FFmpeg found in PATH: {ffmpeg_path}')
			self.location = ffmpeg_path
			self.available = True
			return True

		standard_paths = [
			'/usr/bin/ffmpeg',
			'/usr/local/bin/ffmpeg',
			'/opt/ffmpeg/bin/ffmpeg',
			'C:\\ffmpeg\\bin\\ffmpeg.exe',
			'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',
		]

		for path in standard_paths:
			if os.path.exists(path):
				logger.info(f'ffmpeg found at: {path}')
				self.location = path
				self.available = True
				return True

		logger.warning('FFmpeg not found in system - videos will be downloaded in original format')
		self.available = False
		return False

	def get_ffmpeg_path(self) -> Optional[str]:
		return self.location if self.available else None

	def configure_ydl_options(self, base_options: dict) -> dict:
		options = base_options.copy()

		if self.available and self.config.enable_video_conversion:
			options['postprocessors'] =[{
				'key': 'FFmpegVideoConvertor',
				'preferedformat': 'mp4',
			}]
			if self.location:
				options['ffmpeg_location'] = self.location
			logger.info('Video conversion to MP4 enabled')
		else:
			options.pop('postprocessors', None)
			options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
			logger.info('Video conversion disabled, downloading in original format')

		return options
