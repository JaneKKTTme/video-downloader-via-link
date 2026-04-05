from abc import ABC, abstractmethod
from typing import Optional, List


class DownloadStrategy(ABC):

	@abstractmethod
	def execute(self, url: str) -> bool:
		pass

	@property
	@abstractmethod
	def name(self) -> str:
		pass


class VideoExtractor(ABC):

	@abstractmethod
	def execute(self, url: str) -> Optional[List[str]]:
		pass
