import logging
import sys
from typing import Optional


def setup_logger(
	name: str = 'video_downloader',
	level: int = logging.INFO,
	log_format: Optional[str] = None
) -> logging.Logger:
	"""Configure and return a logger instance.
	
	This function creates a logger with console output and configurable
	format and log level. It prevents duplicate handlers by checking
	if the logger already has handlers attached.
	
	Args:
		name: Logger name, typically __name__ of the calling module.
		level: Logging level (e.g., logging.INFO, logging.DEBUG).
		log_format: Custom log format string. If None, uses default format.
		
	Returns:
		Configured logger instance.
		
	Examples:
		>>> logger = setup_logger(__name__)
		>>> logger.info("Video download started")
		2024-01-01 12:00:00 - module_name - INFO - Video download started
		
		>>> debug_logger = setup_logger("debugger", level=logging.DEBUG)
		>>> debug_logger.debug("Detailed debug message")
	"""
	
	if log_format is None:
		log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

	logger = logging.getLogger(name)
	logger.setLevel(level)

	if logger.handlers:
		return logger

	handler = logging.StreamHandler(sys.stdout)
	handler.setLevel(level)

	formatter = logging.Formatter(log_format)
	handler.setFormatter(formatter)

	logger.addHandler(handler)

	return logger
