from PIL import Image
import imagehash
from io import BytesIO

def compute_phash(image_bytes: bytes, hash_size: int = 16) -> str:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    return str(imagehash.phash(img, hash_size=hash_size))

def phash_hamming_distance(hex1: str, hex2: str) -> int:
    return (int(hex1, 16) ^ int(hex2, 16)).bit_count()
