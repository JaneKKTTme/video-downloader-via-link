from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.schemas import DownloadResponse, DownloadRequest
from app.api.dependencies import get_downloader
from app.core.downloader import VideoDownloader
from app.core.exceptions import DownloadError, NetworkError, BrowserError, FFmpegError
from app.utils.logger import setup_logger


logger = setup_logger(__name__)

router = APIRouter()

@router.post('/download')
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



def download_video_form(
	url: str = Form(...),
	downloader: VideoDownloader = Depends(get_downloader)
):
	try:
		validated = DownloadRequest(url=url)
		url = str(validated.url)
		logger.info(f'Download request received for: {url}')

		success = downloader.download(url)
		if success:
			from urllib.parse import quote
			encoded_url = quote(url, safe='')

			return RedirectResponse(
				url=f'/?link={encoded_url}&result=true&success=true&message=Video+downloaded+successfully&file_path=downloads/video_from_{url[:50]}',
				status_code=303
			)
		else:
			return RedirectResponse(
				url=f'/?result=true&success=false&message=Download+failed+for+unknown+reason',
				status_code=303
			)

	except DownloadError as e:
		logger.error(f'Download failed: {e}')

		from urllib.parse import quote
		encoded_url = quote(url, safe='')
		encoded_message = quote(str(e), safe='')

		return RedirectResponse(
				url=f'/?link={encoded_url}&result=true&success=false&message={encoded_message}',
				status_code=303
			)
	except Exception as e:
		logger.error(f'Unexpected error: {e}', exc_info=True)
		return RedirectResponse(
				url=f'/?result=true&success=false&message=Internal+server+error',
				status_code=303
			)

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
