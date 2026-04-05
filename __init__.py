__version__ = '1.0.0'
__author__ = 'JaneKKTTme'
__all__ = ['VideoDownloader', 'DownloaderConfig', 'DownloadError']

from main import VideoDownloader
from core.config import DownloaderConfig
from core.exceptions import DownloadError