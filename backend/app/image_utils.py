from PIL import Image
import imagehash
from io import BytesIO
from typing import Tuple

def compute_phash(image_bytes: bytes, hash_size: int = 16) -> str:
    """
    Return a hex string of perceptual hash (pHash).
    Using imagehash.phash (which returns ImageHash object).
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    phash = imagehash.phash(img, hash_size=hash_size)
    return phash.__str__()  # hex string, e.g. 'ffab34...'

def phash_hamming_distance(hex1: str, hex2: str) -> int:
    """
    Compute Hamming distance between two hex pHashes.
    """
    # imagehash ImageHash.__str__ returns hex; convert to int
    v1 = int(hex1, 16)
    v2 = int(hex2, 16)
    # get binary XOR and count bits
    x = v1 ^ v2
    return x.bit_count()
