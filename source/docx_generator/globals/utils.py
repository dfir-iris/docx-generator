import os
import shutil
import uuid
from logging import Logger
from typing import Dict

import requests
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from docx_generator.exceptions.rendering_error import RenderingError


def retrieve_remote_file(image_path: str, base_path: str, file_storage_path: str, logger: Logger, proxy_settings: Dict[str, str] = None) -> str:
    """
    Download the image to a local path and return the full path to the image file.
    If it's not a remote file, just return the image_path to process it further
    """
    proxy_settings = proxy_settings if proxy_settings is not None else {}
    requests_proxy_settings = {}
    if proxy_settings is None:
        requests_proxy_settings = {key: value for (key, value) in proxy_settings.items() if key in ['http', 'https']}

    if image_path[:4] != 'http':
        return os.path.abspath(os.path.join(base_path, image_path))

    file_name = os.path.join(file_storage_path, str(uuid.uuid4())) + os.path.splitext(image_path)[1]
    try:
        res = requests.get(image_path, stream=True, timeout=2, proxies=requests_proxy_settings)
        if res.status_code == 200:
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(res.raw, f)
            logger.debug('Image downloaded: {} to {}'.format(image_path, file_name))
        else:
            raise RenderingError(logger, 'Image could not be downloaded, status {}: {}'.format(res.status_code, image_path))

    except Exception as e:
        raise RenderingError(logger, e.__str__())

    return file_name


def resize_image(image, new_width):
    aspect_ratio = float(image.height) / float(image.width)

    image.width = new_width
    image.height = int(aspect_ratio * new_width)


def get_available_paragraph_alignments():
    return list(WD_PARAGRAPH_ALIGNMENT.__members__.keys())