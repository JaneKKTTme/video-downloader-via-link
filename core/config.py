import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BrowserConfig:
	page_load_timeout: int = int(os.getenv('PAGE_LOAD_TIMEOUT', 30))
	page_load_delay: int = int(os.getenv('PAGE_LOAD_DELAY', 5))
	network_wait_timeout: int = int(os.getenv('NETWORK_WAIT_TIMEOUT', 20))
	button_wait_timeout: int = int(os.getenv('BUTTON_WAIT_TIMEOUT', 5))
	scroll_distance: int = 10_000
	headless_mode: bool = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'

	chrome_options: List[str] = field(default_factory=lambda: [
		'--no-sandbox',
		'--headless',
		'--disable-setuid-sandbox',
		'--disable-namespace-sandbox',
		'--disable-dev-shm-usage',
		'--disable-gpu',		

		'--single-process',
		'--disable-accelerated-2d-canvas',
		'--disable-accelerated-jpeg-decoding',
		'--disable-accelerated-mjpeg-decode',
		'--disable-accelerated-video-decode',
		'--disable-webgl',
		'--disable-software-rasterizer',

		'--memory-pressure-off',
		'--max_old_space_size=512',
		'--disable-logging',
		'--log-level=3',
		'--silent',

		'--disable-crash-reporter',
		'--disable-breakpad',
		
		'start-maximized',
		'--autoplay-policy=no-user-gesture-required',
		'disable-infobars',
		'--disable-extensions',
		'--disable-plugins',
		'--disable-default-apps',
		'--ignore-certificate-errors',
		'--mute-audio',
		'--disable-notifications',
		'--disable-popup-blocking',
	])

	play_button_xpaths: List[str] = field(default_factory=lambda: [
		'//button[contains(@title, "Смотреть")]',
		'//button[contains(@title, "Воспроизвести")]',
		'//button[contains(@data-tooltip-title, "Смотреть")]',
		'//button[contains(@data-tooltip-title, "Воспроизвести")]',
		'//button[contains(@aria-label, "Воспроизведение")]',
		'//button[.//span[.//span[contains(text(), "Смотреть") or contains(text(), "Воспроизвести")]]]'
	])


@dataclass
class DownloaderConfig:
	browser: BrowserConfig = field(default_factory=BrowserConfig)
	enable_video_conversion: bool = os.getenv('ENABLE_VIDEO_CONVERSION', 'true').lower() == 'true'
	ffmpeg_location: Optional[str] = os.getenv('FFMPEG_LOCATION', None)
	cookie_file: str = os.getenv('COOKIE_FILE', 'cookies.txt')
	download_path: str = os.getenv('DOWNLOAD_PATH', 'downloads')

	ydl_retries: int = int(os.getenv('YDL_RETRIES', 10))
	fragment_retries: int = int(os.getenv('FRAGMENT_RETRIES', 10))
	wait_for_video: int = int(os.getenv('WAIT_FOR_VIDEO', 30))

	@classmethod
	def from_env(cls) -> 'DownloaderConfig':
		return cls()
