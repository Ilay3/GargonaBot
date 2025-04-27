# convert_images.py
import base64
from pathlib import Path


def encode_images(folder: str, output_file: str):
    images = {}
    for img_path in Path(folder).glob("**/*"):
        if img_path.is_file():
            with open(img_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                key = str(img_path.relative_to(folder)).replace("\\", "/")
                images[key] = data

    with open(output_file, "w") as f:
        f.write("IMAGES = {\n")
        for k, v in images.items():
            f.write(f'    "{k}": "{v}",\n')
        f.write("}\n")


if __name__ == "__main__":
    encode_images("resources/images", "src/encoded_images.py")