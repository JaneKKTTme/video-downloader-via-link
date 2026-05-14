"""Services module containing browser automation and download strategies.

This module provides the core services for browser management, FFmpeg handling,
and various download strategies.
"""

from services.browser_service import BrowserService
from services.ffmpeg_manager import FFmpegManager
from services.strategies import (
	YtdlpStrategy,
	NetworkCaptureStrategy,
	DirectLinkStrategy
)

__all__ = [
	'BrowserService',
	'FFmpegManager',
	'YtdlpStrategy',
	'NetworkCaptureStrategy',
	'DirectLinkStrategy'
]
