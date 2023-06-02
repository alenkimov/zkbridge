import json
import io
from typing import Any
from pathlib import Path

import numpy
from PIL import Image


def to_json(obj: Any) -> str:
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


def load_json(filepath: Path) -> dict:
    if filepath.exists():
        with open(filepath, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError(filepath)


def get_random_image() -> bytes:
    imarray = numpy.random.rand(100, 100, 3) * 255
    image = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    return img_bytes
