from PIL import Image
from PIL.ExifTags import TAGS


def extract_metadatda(img_path: str):
    img = Image.open(img_path)
    info = img.getexif()

    for tag_id in info:
        name = TAGS.get(tag_id, tag_id)
        val = info.get(tag_id)
        print(f"{name}: {val}")

extract_metadatda("img.jpg")