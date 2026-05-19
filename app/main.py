from urllib.parse import unquote

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1 import health
from app.api.v1 import download


app = FastAPI(
	title='Video Downloader',
	description='Download videos from websites using multiple strategies',
	version='1.0.0'
)

templates = Jinja2Templates(directory='app/templates')

app.include_router(health.router, tags=['health'])
app.include_router(download.router, tags=['download'])

app.mount('/static', StaticFiles(directory='app/static'), name='static')


@app.get('/')
async def root(
	request: Request,
	link: str = None,
	result: bool = False,
	success: bool = False,
	message: str = None,
	file_path: str = None
):
	if link:
		link = unquote(link)
	if message:
		message = unquote(message)

	context_data = {
		'request': request,
		'link': link,
		'result': result, 
		'success': success,
		'message': message,
		'file_path': file_path
	}
	return templates.TemplateResponse('video_downloader_page.html', context_data)
