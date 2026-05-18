from typing import Optional

from pydantic import BaseModel, HttpUrl


class HealthResponse(BaseModel):
	status: str
	version: str
	ffmpeg_availability: bool
	headless_mode: bool
