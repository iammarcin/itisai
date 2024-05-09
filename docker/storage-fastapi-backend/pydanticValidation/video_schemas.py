from pydantic import BaseModel, constr
from typing import List, Optional, Dict, Union

class ImageResizeInput(BaseModel):
    image_file_path: str
    width: int
    height: int
    method: str = "resize"
    customerId: Optional[int] = 1

class GetImageSizeInput(BaseModel):
    item: Union[str, bytes]
    customerId: Optional[int] = 1

class VerifyDirectoryInput(BaseModel):
    dir_name: str
    customerId: Optional[int] = 1

class CopyFilesInput(BaseModel):
    files_list: List[str]
    dir_name: str
    customerId: Optional[int] = 1

class ConsistencyCheckInput(BaseModel):
    image_files: List[str]
    audio_files: List[str]
    customerId: Optional[int] = 1

class ConcatFilesInput(BaseModel):
    input_videos_list: List[str]
    output_video_name: str
    dir: str = "./"
    customerId: Optional[int] = 1

class FadeEffectInput(BaseModel):
    input_file_path: str
    output_file_path: str
    effect: str = 'in'
    length: int = 30
    start_frame: int = 0
    dir_path: str = './'
    customerId: Optional[int] = 1

class MergeAudioVideoInput(BaseModel):
    video_path: str
    audio_path: str
    output_path: str
    directory_path: Optional[str] = "./"
    customerId: Optional[int] = 1

class GetAudioFileDurationInput(BaseModel):
    input_audio_name: str
    dir: Optional[str] = "."
    customerId: Optional[int] = 1

class GenerateZoomVideoInput(BaseModel):
    filename: str
    videoLength: float
    width: int
    height: int
    outputFileName: str = "output.mp4"
    method: str = "zoomCenter"
    dir: str = "./"
    customerId: Optional[int] = 1