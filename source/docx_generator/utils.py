import uuid
from typing import Callable

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


def resize_image(image, new_width):
    aspect_ratio = float(image.height) / float(image.width)

    image.width = new_width
    image.height = int(aspect_ratio * new_width)


def get_available_paragraph_alignments():
    return list(WD_PARAGRAPH_ALIGNMENT.__members__.keys())


def generate_logger_identifier():
    return uuid.uuid4().hex[:10]
