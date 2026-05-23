"""Core module containing main business logic.

This module provides core classes for configuration, downloading,
and custom exceptions.
"""

from app.core.config import DownloaderConfig, BrowserConfig
from app.core.downloader import VideoDownloader
from app.core.exceptions import (
	DownloadError,
	BrowserError,
	FFmpegError,
	NetworkError,
	DownloadTimeoutError,
)
from app.core.interfaces import DownloadStrategy, VideoExtractor

__all__ = [
	'DownloaderConfig',
	'BrowserConfig',
	'VideoDownloader',
	'DownloadError',
	'BrowserError',
	'FFmpegError',
	'NetworkError',
	'DownloadTimeoutError',
	'DownloadStrategy',
	'VideoExtractor',
]
