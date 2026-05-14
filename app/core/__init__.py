"""Core module containing configuration and exception classes.

This module exports the main configuration and exception classes used
throughout the video downloader application.
"""

from core.config import DownloaderConfig, BrowserConfig
from core.exceptions import (
	VideoDownloaderError,
	ConfigurationError,
	BrowserError,
	DownloadError,
	FFmpegError,
	NetworkError,
	DownloadTimeoutError
)

__all__ = [
	'DownloaderConfig',
	'BrowserConfig',

	'VideoDownloaderError',
	'ConfigurationError',
	'BrowserError',
	'DownloadError',
	'FFmpegError',
	
	'NetworkError',
	'DownloadTimeoutError'
]
