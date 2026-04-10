import json
import time
import shutil
import sys
import os
from contextlib import contextmanager
from typing import List, Optional, Generator
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from core.config import DownloaderConfig
from core.exceptions import BrowserError, DownloadTimeoutError
from utils.logger import setup_logger


logger = setup_logger(__name__)


class BrowserService:
	"""Service for browser automation and video URL extraction.
	
	This class manages Chrome WebDriver instances and provides methods
	to capture network traffic and extract video URLs from web pages.
	
	Attributes:
		config: Downloader configuration containing browser settings.
		use_webdriver_manager: Whether to use webdriver-manager for driver binary.
		driver_path: Path to ChromeDriver executable.
	"""

	def __init__(self, config: DownloaderConfig, use_webdriver_manager: bool = True):
		"""Initialize the browser service.
		
		Args:
			config: Downloader configuration with browser settings.
			use_webdriver_manager: If True, use webdriver-manager to handle driver binary.
		"""
		self.config = config
		self.use_webdriver_manager = use_webdriver_manager
		self.driver_path = self._get_driver_path()

	@contextmanager
	def create_driver(self) -> Generator[webdriver.Chrome, None, None]:
		"""Create and manage a Chrome WebDriver instance as a context manager.
		
		Yields:
			Configured Chrome WebDriver instance.
			
		Raises:
			BrowserError: If WebDriver creation fails.
			
		Examples:
			>>> with browser_service.create_driver() as driver:
			...	 	driver.get("https://example.com")
			...	 	# Driver automatically quits after block
		"""
		options = self._get_chrome_options()
		driver = None
		try:
			driver = webdriver.Chrome(
				service=Service(self.driver_path),
				options=options
			)
			driver.set_page_load_timeout(self.config.browser.page_load_timeout)
			logger.debug('WebDriver created successfully')
			yield driver

		except WebDriverException as e:
			logger.error(f'WebDriver error: {e}')
			raise BrowserError(f'Failed to create WebDriver: {e}')
		finally:
			if driver:
				driver.quit()
				logger.debug('WebDriver closed')

	def _get_driver_path(self) -> str:
		"""Determine the ChromeDriver path to use.
		
		Checks Docker paths first, then falls back to webdriver-manager or system PATH.
		
		Returns:
			Path to ChromeDriver executable.
			
		Examples:
			>>> path = browser_service._get_driver_path()
			>>> print(path)
			'/usr/local/bin/chromedriver'
		"""
		docker_paths = [
			'/usr/local/bin/chromedriver',
			'/usr/bin/chromedriver',
		]
		
		for path in docker_paths:
			if os.path.exists(path):
				logger.info(f'Using Docker ChromeDriver: {path}')
				return path
		
		if self.use_webdriver_manager:
			try:
				driver_path = ChromeDriverManager().install()
				logger.info(f'Using webdriver-manager ChromeDriver: {driver_path}')
				return driver_path
			except Exception as e:
				logger.warning(f'webdriver-manager failed: {e}, falling back to PATH')
		
		return 'chromedriver'

	def _get_chrome_options(self) -> webdriver.ChromeOptions:
		"""Configure Chrome browser options.
		
		Returns:
			ChromeOptions object with configured arguments and capabilities.
		"""
		options = webdriver.ChromeOptions()

		for arg in self.config.browser.chrome_options:
			options.add_argument(arg)

		if self.config.browser.headless_mode:
			options.add_argument('--headless')
			logger.debug('Running in headless mode')

		if sys.platform == 'win32':
			options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
			options.add_experimental_option('useAutomationExtension', False)

		chrome_binary = self._find_chrome_binary()
		if chrome_binary:
			options.binary_location = chrome_binary
			logger.debug(f'Using Chrome library: {chrome_binary}')

		options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

		return options

	def _find_chrome_binary(self) -> str:
		"""Locate Chrome browser executable on the system.
		
		Returns:
			Path to Chrome executable, or None if not found.
		"""
		chrome_paths = []
	
		if sys.platform == 'win32':
			chrome_paths = [
				r'C:\Program Files\Google\Chrome\Application\chrome.exe',
				r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
				r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(
					os.getenv('USERNAME')
				),
			]
		elif sys.platform == 'darwin':
			chrome_paths = [
				'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
			]
		else:
			chrome_paths = [
				'/usr/bin/google-chrome',
				'/usr/bin/google-chrome-stable',
				'/opt/google/chrome/google-chrome',
			]

		for path in chrome_paths:
			if os.path.exists(path):
				return path
		
		chrome_cmd = shutil.which('google-chrome') or shutil.which('chrome')
		if chrome_cmd:
			return chrome_cmd
		
		logger.warning('Chrome binary not found')
		return None

	def capture_network_videos(self, url: str) -> List[str]:
		"""Capture video URLs from network traffic.
		
		Loads the page, scrolls, clicks play button, and extracts video URLs
		from performance logs.
		
		Args:
			url: Web page URL to analyze.
			
		Returns:
			List[str]: List of unique video URLs found in network traffic.
			
		Examples:
			>>> urls = browser_service.capture_network_videos("https://example.com/video")
			>>> print(f"Found {len(urls)} video streams")
		"""
		with self.create_driver() as driver:
			try:
				driver.get(url)

				WebDriverWait(driver, self.config.browser.page_load_timeout).until(
					ec.presence_of_element_located((By.TAG_NAME, 'body'))
				)

				driver.execute_script(
					f'window.scrollTo(0, {self.config.browser.scroll_distance})'
				)
				time.sleep(self.config.browser.page_load_delay)

				if self._click_play_button(driver):
					logger.debug('Play button clicked')
				else:
					logger.warning('Play button not found or not clickable')

				logger.debug(f'Waiting {self.config.browser.network_wait_timeout}s for video to load...')
				time.sleep(self.config.browser.network_wait_timeout)

				return self._extract_video_urls(driver)

			except TimeoutException as e:
				logger.error(f'Timeout while loading page: {e}')
				return []
			except Exception as e:
				logger.error(f'Network capture error: {e}')
				return []

	def _click_play_button(self, driver: webdriver.Chrome) -> bool:
		"""Attempt to click play button using configured XPath patterns.
		
		Args:
			driver: Chrome WebDriver instance.
			
		Returns:
			bool: True if a play button was found and clicked, False otherwise.
		"""
		wait = WebDriverWait(driver, self.config.browser.button_wait_timeout)

		for xpath in self.config.browser.play_button_xpaths:
			try:
				button = wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
				button.click()
				logger.debug(f'Click on button: {xpath}')
				return True
			except TimeoutException:
				continue

		logger.debug('No play button found')
		return False

	def _extract_video_urls(self, driver: webdriver.Chrome) -> List[str]:
		"""Extract video URLs from browser performance logs.
		
		Args:
			driver: Chrome WebDriver instance.
			
		Returns:
			List[str]: List of unique video URLs found in network logs.
		"""
		available_logs = driver.log_types
		if 'performance' not in available_logs:
			logger.error('Performance logs not available')
			return []

		logs = driver.get_log('performance')
		video_urls = []

		for log in logs:
			try:
				network_log = json.loads(log['message'])['message']

				if not any(method in network_log['method'] for method in \
						['Network.response', 'Network.request', 'Network.webSocket']):
					continue

				url_log = network_log['params'].get('request', {}).get('url', '')

				if self._is_video_url(url_log):
					video_urls.append(url_log)

			except (json.JSONDecodeError, KeyError) as e:
				logger.debug(f'Error parsing log: {e}')
				continue

		unique_urls = list(set(video_urls))
		logger.info(f'Found {len(unique_urls)} unique video URLs')

		return unique_urls

	def _is_video_url(self, url: str) -> bool:
		"""Check if URL points to video content.
		
		Args:
			url: URL to check.
			
		Returns:
			bool: True if URL appears to be a video stream, False otherwise.
		"""
		video_extensions = ['m3u8', 'mp4']
		video_patterns = ['master', 'index']

		url_lower = url.lower()

		has_extension = any(ext in url_lower for ext in video_extensions)
		has_pattern = any(pattern in url_lower for pattern in video_patterns)
		is_blob = 'blob' in url_lower

		return has_extension and has_pattern and not is_blob

	def find_direct_video_urls(self, url: str) -> List[str]:
		"""Find direct video URLs in page HTML.
		
		Searches for video URLs in anchor tags and source elements.
		
		Args:
			url: Web page URL to search.
			
		Returns:
			List[str]: List of unique direct video URLs found on the page.
			
		Examples:
			>>> urls = browser_service.find_direct_video_urls("https://example.com")
			>>> for url in urls:
			...	 	print(f"Direct link: {url}")
		"""
		with self.create_driver() as driver:
			try:
				driver.get(url)
				time.sleep(self.config.browser.page_load_delay)

				video_urls = []

				for link in driver.find_elements(By.TAG_NAME, 'a'):
					href = link.get_attribute('href')
					if href and self._is_video_url(href):
						video_urls.append(href)

				for source in driver.find_elements(By.TAG_NAME, 'source'):
					src = source.get_attribute('src')
					if src and self._is_video_url(src):
						video_urls.append(src)

				return list(set(video_urls))

			except Exception as e:
				logger.error(f'Error searching video URL on page: {e}')
				return []
