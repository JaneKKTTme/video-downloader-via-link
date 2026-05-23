"""API module containing versioned endpoints.

This module exports the main API router and version-specific modules.
"""

from app.api.v1 import health, download

__all__ = ['health', 'download']
