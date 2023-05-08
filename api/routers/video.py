import logging
from fastapi import APIRouter, File, UploadFile
from common.exceptions import ApplicationError, ErrorCode
# from video.entity import VideoEntity, VideoMeta
# from video.service import VideoService


# logger = logging.getLogger(__name__)
# router = APIRouter()
# video_service = VideoService()


# @router.post('/video', response_model=VideoMeta)
# async def upload_video(file: UploadFile = File(...)):

#     if file.content_type != 'video/mp4':
#         raise ApplicationError(code=ErrorCode.APPLICATION_ERROR, message='파일 형식 오류', description='mp4 파일만 업로드 가능합니다.')

#     video = VideoEntity(file=file.file)
#     video_meta = video_service.upload_video(video=video)

#     return video_meta
