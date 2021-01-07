import zipfile
import io

def extract_all(content: bytes, abs_path: str):
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        z.extractall(abs_path)