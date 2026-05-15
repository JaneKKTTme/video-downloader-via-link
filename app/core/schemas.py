from typing import Optional


class HealthResponse(BaseModel):
	status: str
	version: str
	ffmpeg_availability: bool
	headless_mode: bool
