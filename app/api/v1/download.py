from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.schemas import DownloadResponse, DownloadRequest
from app.api.dependencies import get_downloader
from app.core.downloader import VideoDownloader
from app.core.exceptions import DownloadError, NetworkError, BrowserError, FFmpegError
from app.utils.logger import setup_logger


logger = setup_logger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory='app/templates')

def validate_url_basic(url: str) -> tuple[bool, str]:
	if not url or not url.strip():
		return False, 'Пожалуйста, введите ссылку на видео'
	
	if not url.startswith(('http://', 'https://')):
		return False, 'Некорректная ссылка. URL должен начинаться с http:// или https://'
	
	if len(url) < 10:
		return False, 'Слишком короткая ссылка. Проверьте правильность ввода'
	
	forbidden = ["'", '"', '<', '>', ';', '`']
	if any(char in url for char in forbidden):
		return False, 'Ссылка содержит недопустимые символы'
	
	return True, 'OK'

def validate_url_pydantic(url: str) -> tuple[bool, str]:
	try:
		validated = DownloadRequest(url=url)
		return True, str(validated.url)
	except ValidationError as e:
		errors = e.errors()
		if errors:
			error_msg = errors[0].get('msg', 'Неверный формат URL')
			return False, f'Ошибка в ссылке: {error_msg}'
		return False, 'Неверный формат ссылки'

def get_user_friendly_message(error: Exception) -> str:
	error_str = str(error).lower()
	
	if isinstance(error, DownloadError):
		if 'invalid url' in error_str or 'url' in error_str:
			return 'Некорректная ссылка. Пожалуйста, проверьте URL и попробуйте снова.'
		elif 'timeout' in error_str:
			return 'Превышено время ожидания. Возможно, видео загружается слишком долго или сайт недоступен.'
		elif 'not found' in error_str:
			return 'Видео не найдено. Проверьте, доступен ли ролик по указанной ссылке.'
	
	elif isinstance(error, NetworkError):
		return 'Ошибка сети. Проверьте интернет-соединение и попробуйте снова.'
	
	elif isinstance(error, BrowserError):
		return 'Не удалось загрузить страницу. Возможно, сайт требует авторизации или временно недоступен.'
	
	elif isinstance(error, FFmpegError):
		return 'Ошибка конвертации видео. Файл будет сохранён в оригинальном формате.'
	
	elif 'yt-dlp' in error_str or 'youtube' in error_str:
		return 'Не удалось загрузить видео с YouTube. Возможно, видео имеет ограничения или требует авторизации.'
	
	return f'Произошла ошибка: {str(error)}'



@router.post('/download', response_class=HTMLResponse)
def download_video_form(
	request: Request,
	url: str = Form(...),
	downloader: VideoDownloader = Depends(get_downloader)
):
	context_data = {
		'request': request,
		'url': url,
	}

	is_valid, error_message = validate_url_basic(url)
	if not is_valid:
		context_data['result'] = True
		context_data['success'] = False
		context_data['message'] = error_message
		logger.warning(f'URL validation failed (basic): {url} - {error_message}')
		return templates.TemplateResponse('video_downloader_page.html', context_data)

	is_valid, error_message = validate_url_pydantic(url)
	if not is_valid:
		context_data['result'] = True
		context_data['success'] = False
		context_data['message'] = error_message
		logger.warning(f'URL validation failed (pydantic): {url} - {error_message}')
		return templates.TemplateResponse('video_downloader_page.html', context_data)

	try:
		logger.info(f'Download request received for: {url}')

		success = downloader.download(url)
		if success:
			context_data['result'] = True
			context_data['success'] = True
			context_data['message'] = 'Видео успешно загружено!'
			context_data['file_path'] = f'downloads/video_from_{url[:50]}'
			logger.info(f'Video downloaded successfully from {url}')
		else:
			context_data['result'] = True
			context_data['success'] = False
			context_data['message'] = 'Не удалось загрузить видео. Попробуйте другую ссылку.'
			logger.info(f'Failed to load video from {url}')

	except DownloadError as e:
		logger.error(f'Download failed: {e}')
		context_data['result'] = True
		context_data['success'] = False
		context_data['message'] = get_user_friendly_message(e)

	except NetworkError as e:
		logger.error(f'Network error: {e}')
		context_data['result'] = True
		context_data['success'] = False
		context_data['message'] = get_user_friendly_message(e)

	except BrowserError as e:
		logger.error(f'Browser error: {e}')
		context_data['result'] = True
		context_data['success'] = False
		context_data['message'] = get_user_friendly_message(e)

	except Exception as e:
		logger.error(f'Unexpected error: {e}', exc_info=True)
		context_data['result'] = True
		context_data['success'] = False
		context_data['message'] = 'Неожиданная ошибка. Попробуйте, пожалуйста, позже.'

	return templates.TemplateResponse('video_downloader_page.html', context_data)
		
@router.post('/api/download', response_model=DownloadResponse)
def download_video_api(
	request: DownloadRequest,
	downloader: VideoDownloader = Depends(get_downloader)
):
	try:
		logger.info(f'API download request received for: {request.url}')

		success = downloader.download(str(request.url))
		if success:
			return DownloadResponse(
				success=True,
				message='Video downloaded successfully',
				file_path=f'downloads/video_from_{str(request.url)[:50]}'
			)
		else:
			raise HTTPException(status_code=500, detail='Download failed for unknown reason')

	except DownloadError as e:
		logger.error(f'Download failed: {e}')
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		logger.error(f'Unexpected error: {e}', exc_info=True)
		raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')
