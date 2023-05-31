import io
from pathlib import Path

import numpy
from PIL import Image


def get_random_image() -> bytes:
    imarray = numpy.random.rand(100, 100, 3) * 255
    image = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    return img_bytes
