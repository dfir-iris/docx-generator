import os
import shutil
import uuid
from logging import Logger

import requests

from docx_generator.exceptions.rendering_error import RenderingError


def retrieve_remote_file(image_path: str, base_path: str, file_storage_path: str, logger: Logger) -> str:
    """
    Download the image to a local path and return the full path to the image file.
    If it's not a remote file, just return the image_path to process it further
    """
    if image_path[:4] != 'http':
        return os.path.abspath(os.path.join(base_path, image_path))

    file_name = os.path.join(file_storage_path, str(uuid.uuid4())) + os.path.splitext(image_path)[1]
    try:

        res = requests.get(image_path, stream=True, timeout=2)
        if res.status_code == 200:
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(res.raw, f)
            logger.debug('Image downloaded: {} to {}'.format(image_path, file_name))
        else:
            raise RenderingError(logger, 'Image could not be downloaded, status {}: {}'.format(res.status_code, image_path))

    except Exception as e:
        raise RenderingError(logger, e.__str__())

    return file_name
