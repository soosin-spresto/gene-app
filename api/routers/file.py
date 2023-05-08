import logging
from typing import List, Any, Optional
from fastapi import APIRouter, File, UploadFile
from pydantic.main import BaseModel
from PIL import Image, ImageFile
from io import BytesIO
from common.utils import generate_key


logger = logging.getLogger(__name__)
router = APIRouter()
CLOUD_STORAGE_BUCKET = 'goldhand'


class ImageEntity(BaseModel):
    file: Any
    content_type: str = ""


@router.post('/file/image', response_model=List[str])
def upload_image(is_mini: bool = False, files: List[UploadFile] = File(...)):
    return
    urls = []
    for f in files:
        image = ImageEntity(file=f.file, content_type=f.content_type)

        converted_img = _convert_image(image=image)
        if converted_img:
            new_file_name = f'{generate_key(length=5)}.jpg'
            urls.append(_upload_image(image=converted_img, filepath='img/' + new_file_name))

            if is_mini:
                resized_img = _convert_image(image=image, is_resize=True)
                if resized_img:
                    _upload_image(image=resized_img, filepath=f'img/mini/{new_file_name}')

    return urls


def _convert_image(image: ImageEntity, is_resize: bool = False) -> Optional[ImageEntity]:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    # TODO : 여기서 메타데이터, 특히 위치 정보도 딸 수 있나?
    try:
        orig = Image.open(image.file)
        orig = orig.convert("RGB")
        img = BytesIO()

        if is_resize:
            orig.thumbnail((80, 80), Image.ANTIALIAS)
            orig.save(img, "JPEG", quality=90)
        else:
            orig.save(img, "JPEG", quality=90)

        img.seek(0)
        return ImageEntity(file=img, content_type=Image.MIME["JPEG"])
    except Exception:
        return None
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False


def _upload_image(image: ImageEntity, filepath: str) -> str:
    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(filepath)
    blob.upload_from_string(image.file.read(), content_type=image.content_type)

    return blob.public_url
