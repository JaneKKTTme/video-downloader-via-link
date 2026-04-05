import logging
import sys
from typing import Optional


def setup_logger(
	name: str = 'video_downloader',
	level: int = logging.INFO,
	log_format: Optional[str] = None
) -> logging.Logger:
	
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
