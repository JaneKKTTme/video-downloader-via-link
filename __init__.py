"""Video Downloader - A robust tool for downloading videos from websites.

This package provides multiple strategies for video extraction and download,
including yt-dlp integration, network traffic capture, and direct link extraction.

Example:
	>>> from video_downloader import VideoDownloader
	>>> downloader = VideoDownloader()
	>>> downloader.download("https://example.com/video")
"""

__version__ = '1.0.0'
__author__ = 'JaneKKTTme'
__all__ = ['VideoDownloader', 'DownloaderConfig', 'DownloadError']

from main import VideoDownloader
from core.config import DownloaderConfig
from core.exceptions import DownloadError
