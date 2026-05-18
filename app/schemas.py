from typing import Optional

from pydantic import BaseModel, HttpUrl


class DownloadRequest(BaseModel):
	url: HttpUrl

	class Config:
		json_schema_extra = {
			'example': {'url': 'https://www.youtube/com/watch?v=...'}
		}

class DownloadResponse(BaseModel):
	success: bool
	message: str
	file_path: Optional[str] = None
	error: Optional[str] = None

class HealthResponse(BaseModel):
	status: str
	version: str
	ffmpeg_availability: bool
	headless_mode: bool
