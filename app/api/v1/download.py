from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse

from app.schemas import DownloadResponse, DownloadRequest
from app.api.dependencies import get_downloader
from app.core.downloader import VideoDownloader
from app.core.exceptions import DownloadError
from app.utils.logger import setup_logger


logger = setup_logger(__name__)

router = APIRouter()

@router.post('/download')
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
