class VideoDownloaderError(Exception):
	"""Base exception for all video downloader related errors.
	
	This is the parent class for all custom exceptions in the video downloader.
	It wraps original exceptions to provide additional context.
	
	Attributes:
		message: Human-readable error description.
		original_exception: The original exception that was caught, if any.
	
	Examples:
		>>> try:
		...	 raise VideoDownloaderError("Something went wrong")
		... except VideoDownloaderError as e:
		...	 print(str(e))
		'Something went wrong'
	"""

	def __init__(self, message: str, original_exception: Exception = None):
		"""Initialize the exception with a message and optional original exception.
		
		Args:
			message: Human-readable error description.
			original_exception: The original exception that was caught.
		"""
		super().__init__(message)
		self.original_exception = original_exception


class ConfigurationError(VideoDownloaderError):
	"""Raised when invalid or missing configuration is detected.
	
	Examples:
		>>> raise ConfigurationError("FFmpeg not found in system")
	"""
	pass


class BrowserError(VideoDownloaderError):
	"""Raised when browser automation fails unexpectedly.
	
	Examples:
		>>> raise BrowserError("Failed to initialize Chrome driver")
	"""
	pass


class DownloadError(VideoDownloaderError):
	"""Raised when video download operation fails.
	
	Examples:
		>>> raise DownloadError("All download strategies failed")
	"""
	pass


class FFmpegError(VideoDownloaderError):
	"""Raised when FFmpeg operations fail during video processing.
	
	Examples:
		>>> raise FFmpegError("Failed to convert video to MP4")
	"""
	pass


class NetworkError(VideoDownloaderError):
	"""Raised when network-related operations fail.
	
	Examples:
		>>> raise NetworkError("Connection timeout while fetching video")
	"""
	pass


class DownloadTimeoutError(NetworkError):
	"""Raised when operations exceed configured time limits.
	
	Examples:
		>>> raise DownloadTimeoutError("Page load exceeded 30 second limit")
	"""
	pass
