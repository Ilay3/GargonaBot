import base64
from io import BytesIO
from PIL import Image

# Автоматически сгенерированный файл
from encoded_images import IMAGES


class ImageLoader:
    @staticmethod
    def get_image(image_path: str) -> Image.Image:
        if image_path not in IMAGES:
            raise FileNotFoundError(f"Image {image_path} not found in embedded resources")

        raw_data = base64.b64decode(IMAGES[image_path])
        return Image.open(BytesIO(raw_data))

    @staticmethod
    def get_image_bytes(image_path: str) -> bytes:
        return base64.b64decode(IMAGES[image_path])