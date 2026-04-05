class VideoDownloaderError(Exception):
	"""Base exception for all video downloader related errors."""

	def __init__(self, message: str, original_exception: Exception = None):
		super().__init__(message)
		self.original_exception = original_exception


class ConfigurationError(VideoDownloaderError):
	"""Raised when invalid or missing configuration is detected."""
	pass


class BrowserError(VideoDownloaderError):
	"""Raised when browser automation fails unexpectedly."""
	pass


class DownloadError(VideoDownloaderError):
	"""Raised when video download operation fails."""
	pass


class FFmpegError(VideoDownloaderError):
	"""Raised when FFmpeg operations fail during video processing."""
	pass


class NetworkError(VideoDownloaderError):
	"""Raised when network-related operations fail."""
	pass


class DownloadTimeoutError(NetworkError):
	"""Raised when operations exceed configured time limits."""
	pass
