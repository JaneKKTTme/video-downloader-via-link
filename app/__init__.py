"""Video Downloader - Web API for downloading videos from websites.

This package provides multiple strategies for video extraction and download,
including yt-dlp integration, network traffic capture, and direct link extraction.
"""

__version__ = '1.0.0'
__author__ = 'JaneKKTTme'

from app.core.config import DownloaderConfig
from app.core.downloader import VideoDownloader
from app.core.exceptions import DownloadError, NetworkError, BrowserError, FFmpegError

__all__ = [
	'DownloaderConfig',
	'VideoDownloader',
	'DownloadError',
	'NetworkError',
	'BrowserError',
	'FFmpegError',
	'__version__',
	'__author__',
]
