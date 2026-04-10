import shutil
import os
from typing import Optional

from core.config import DownloaderConfig
from core.exceptions import FFmpegError
from utils.logger import setup_logger


logger = setup_logger(__name__)


class FFmpegManager:
	"""Manages FFmpeg availability and configuration for video processing.
	
	This class handles FFmpeg binary detection and provides configuration
	for yt-dlp to use FFmpeg for video conversion and downloading.
	
	Attributes:
		config: Downloader configuration.
		available: Whether FFmpeg is available on the system.
		location: Path to FFmpeg executable, if found.
	"""

	def __init__(self, config: DownloaderConfig):
		"""Initialize FFmpeg manager and check for FFmpeg availability.
		
		Args:
			config: Downloader configuration with FFmpeg settings.
		"""
		self.config = config
		self.available = False
		self.location: Optional[str] = None
		self._check_ffmpeg()

	def _check_ffmpeg(self) -> bool:
		"""Check if FFmpeg is available on the system.
		
		Searches in configured location, system PATH, and standard paths.
		
		Returns:
			bool: True if FFmpeg is found and usable, False otherwise.
		"""
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
		"""Get the path to FFmpeg executable.
		
		Returns:
			Optional[str]: Path to FFmpeg if available, None otherwise.
		"""
		return self.location if self.available else None

	def configure_ydl_options(self, base_options: dict) -> dict:
		"""Configure yt-dlp options based on FFmpeg availability.
		
		Adds FFmpeg post-processors for video conversion if available.
		
		Args:
			base_options: Base yt-dlp options dictionary.
			
		Returns:
			dict: Modified yt-dlp options with FFmpeg configuration.
			
		Examples:
			>>> base = {'outtmpl': '%(title)s.%(ext)s'}
			>>> options = ffmpeg_manager.configure_ydl_options(base)
			>>> 'postprocessors' in options
			True
		"""
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
