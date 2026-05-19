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
async def root(request: Request):

	context_data = {
		'request': request,
		'link': '',
		'result': False
	}
	return templates.TemplateResponse('video_downloader_page.html', context_data)
