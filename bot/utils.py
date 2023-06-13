import io
import json
import shutil
import tomllib
from pathlib import Path
from typing import Iterable

import numpy
from PIL import Image
from faker import Faker

fake = Faker()


def generate_simple_sentence():
    return fake.sentence(nb_words=3)


def copy_file(source_path: Path, destination_path: Path):
    if destination_path.exists():
        return
    shutil.copy2(str(source_path), str(destination_path))


def to_json(obj) -> str:
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


def rewrite_json(filepath: Path, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def load_json(filepath: Path) -> dict:
    if filepath.exists():
        with open(filepath, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError(filepath)


def rewrite_lines(filepath: Path, lines: Iterable[str]):
    with open(filepath, "w") as file:
        file.write("\n".join(lines))


def load_lines(filepath: Path) -> list[str]:
    if filepath.exists():
        with open(filepath, "r") as file:
            return [line for line in file.readlines() if line != "\n"]
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
