from pathlib import Path
import uuid
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
CARRIER_DIR = UPLOAD_DIR / "carrier"
PAYLOAD_DIR = UPLOAD_DIR / "payload"
OUTPUT_DIR = UPLOAD_DIR / "output"

def ensure_upload_dirs():
    CARRIER_DIR.mkdir(parents=True, exist_ok=True)
    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def unique_filename(original_name: str, prefix: str = ""):
    safe_name = secure_filename(original_name)
    token = uuid.uuid4().hex
    if prefix:
        return f"{token}_{prefix}_{safe_name}"
    return f"{token}_{safe_name}"

def save_bytes(data: bytes, folder: Path, filename: str):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_bytes(data)
    return path

def guess_is_image(filename: str):
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return ext in {"png", "jpg", "jpeg", "gif", "bmp", "webp"}