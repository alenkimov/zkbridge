import tomllib
import json
import io
from pathlib import Path

import numpy
from PIL import Image


def to_json(obj) -> str:
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


def rewrite_json(filepath: Path, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def load_json(filepath: Path) -> dict:
    if filepath.exists():
        with open(filepath, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError(filepath)


def load_toml(filepath: Path) -> dict:
    if filepath.exists():
        with open(filepath, "rb") as file:
            return tomllib.load(file)
    else:
        raise FileNotFoundError(filepath)


def get_random_image() -> bytes:
    imarray = numpy.random.rand(100, 100, 3) * 255
    image = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    return img_bytes
