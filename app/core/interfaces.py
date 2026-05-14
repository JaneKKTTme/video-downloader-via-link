from abc import ABC, abstractmethod
from typing import Optional, List


class DownloadStrategy(ABC):
	"""Abstract base class defining the interface for download strategies.
	
	A download strategy implements a specific method to extract and download
	video content from a given URL.
	"""

	@abstractmethod
	def execute(self, url: str) -> bool:
		"""Execute the download strategy for the given URL.
		
		Args:
			url: The video URL to download from.
			
		Returns:
			bool: True if download succeeded, False otherwise.
			
		Examples:
			>>> strategy = YtdlpStrategy(config, ffmpeg)
			>>> success = strategy.execute("https://example.com/video")
		"""
		pass

	@property
	@abstractmethod
	def name(self) -> str:
		"""Get the name of this download strategy.
		
		Returns:
			str: Human-readable strategy name for logging and debugging.
			
		Examples:
			>>> strategy.name
			'yt-dlp'
		"""
		pass


class VideoExtractor(ABC):
	"""Abstract base class for video URL extraction.
	
	Implementations provide methods to extract video URLs from web pages
	using different techniques like network monitoring or DOM parsing.
	"""

	@abstractmethod
	def execute(self, url: str) -> Optional[List[str]]:
		"""Extract video URLs from the given page URL.
		
		Args:
			url: The web page URL to extract video links from.
			
		Returns:
			Optional[List[str]]: List of video URLs found, or None if extraction failed.
			
		Examples:
			>>> extractor = NetworkExtractor(config)
			>>> urls = extractor.execute("https://example.com/watch")
			>>> print(f"Found {len(urls)} videos")
		"""
		pass
