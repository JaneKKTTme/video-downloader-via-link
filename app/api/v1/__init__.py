"""API v1 module containing version 1 endpoints.

This module exports routers for health check and video download functionality.
"""

from app.api.v1 import health
from app.api.v1.download import router as download_router

# Экспортируем роутеры для удобного включения в main.py
__all__ = [
	'health',
	'download_router',
]
