from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException

import os
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
import shutil
from pytube import YouTube
from typing import Optional
from fastapi.responses import JSONResponse

from google.cloud import storage
storage_client = storage.Client()
bucket_name = 'snowman-bucket'
bucket = storage_client.bucket(bucket_name)


# # google cloud storage
# from google.cloud import storage
# storage_client = storage.Client()
# bucket_name = 'snowman-bucket'
# bucket = storage_client.batch(bucket_name)

from ml.face_functions import FaceClustering


router = APIRouter(tags=["video"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'files/')


class Video(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    file_name: str
    created_at : datetime = Field(default_factory=datetime.now)
    

@router.post("/upload-video", description="비디오를 업로드합니다.")
def create_video_file(file: UploadFile = File(...)):
    new_video = Video(file_name=file.filename)
    # video_contents = await file.read()
    os.makedirs(os.path.join(FILE_DIR, str(new_video.id)))
    id_path = os.path.join(FILE_DIR, str(new_video.id))
    server_path = os.path.join(id_path, ('original' + os.path.splitext(file.filename)[1]))

    with open(server_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    FaceClustering(server_path, os.path.join(id_path, 'result'))
    return new_video


class YTVideo(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    video: Optional[str]
    file_name: str
    created_at : datetime = Field(default_factory=datetime.now)


@router.post("/upload-video-youtube", description="유튜브 URL을 이용하여 비디오를 업로드합니다.")
def create_video_file_from_youtube(info: dict):
    yt_video = YouTube(info['url'])
    new_video = YTVideo(file_name=yt_video.title + '.mp4')

    stream = yt_video.streams.filter(progressive=True, subtype="mp4", resolution="720p").first()
    if stream:
        os.makedirs(os.path.join(FILE_DIR, str(new_video.id)))
        id_path = os.path.join(FILE_DIR, str(new_video.id))
        server_path = os.path.join(id_path, ('original.mp4'))

        stream.download(output_path=id_path, filename='original.mp4')

        # upload to gcs
        blob_dir = os.path.join(str(new_video.id), 'youtube_original.mp4')
        blob = bucket.blob(blob_dir)
        blob.upload_from_filename(server_path)
        new_video.video = os.path.join('https://storage.googleapis.com', bucket_name, blob_dir)

        FaceClustering(server_path, os.path.join(id_path, 'result'))

        return new_video

    else:
        return JSONResponse(
            status_code=422,
            content={"message": "720p를 지원하는 영상이 아닙니다."}
        )
