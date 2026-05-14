from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.v1 import health


app = FastAPI(
	title='Video Downloader',
	description='Download videos from websites using multiple strategies',
	version='1.0.0'
)

app.include_router(health.router, tags=['health'])

@app.get('/')
async def root():
	return FileResponse('./templates/video_downloader_page.html')
