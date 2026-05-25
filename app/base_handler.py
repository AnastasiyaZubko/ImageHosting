from __future__ import annotations

from uuid import uuid4

from PIL import Image
import json
import logging
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from multipart import MultipartPart, MultipartParser, parse_options_header

from app.db_manager import DBManager
from app.settings import STATIC_DIR, IMAGE_EXTENSIONS, MAX_FILE_SIZE, MEDIA_PATH, STATIC_PATH

logger = logging.getLogger(__name__)


class BaseHandler(BaseHTTPRequestHandler):
    server_version = '0.1'
    server_name = 'Image Hosting Server'

    def response(self, data: str | bytes, content_type: str = 'text/html', status_code=200) -> None:
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(
            data if isinstance(data, bytes) else data.encode('utf-8')
        )

    def html_response(self, data: str | bytes, status_code=200) -> None:
        self.response(data, 'text/html', status_code)

    def json_response(self, data: dict | list | str | bytes, status_code=200) -> None:
        if isinstance(data, (dict, list)):
            data = json.dumps(data)
        self.response(data, 'application/json', status_code)

    @staticmethod
    def load_file(filename: str, directory: Path = STATIC_PATH) -> bytes:
        try:
            path = (directory / filename.lstrip('/')).resolve()
            path.relative_to(directory.resolve())

            with open(path, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            return b'Not Found'

    def template_response(self, template_filename: str) -> None:
        self.html_response(self.load_file(template_filename))

    def send_static_file(self, filename: str) -> None:
        if filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.css'):
            content_type = 'text/css'
        elif filename.endswith('.js'):
            content_type = 'text/javascript'
        else:
            content_type = 'application/octet-stream'
        self.response(self.load_file(filename), content_type)

    def send_media_file(self, filename: str) -> None:
        self.response(self.load_file(filename, MEDIA_PATH), content_type='image/png')

    @staticmethod
    def validate_file(file: MultipartPart) -> bool:
        ext = Path(file.filename).suffix.lstrip('.').lower()
        if not ext:
            return False
        if ext.lower() not in IMAGE_EXTENSIONS:
            return False
        if file.size > MAX_FILE_SIZE:
            return False
        temp_file = f'temp.{ext}'
        file.save_as(temp_file)
        try:
            with Image.open(temp_file) as img:
                img.verify()
        except (IOError,SyntaxError):
            return False
        return True

    def parse_multipart(self, content_type: str, options: dict,
                        content_length: int) -> dict | None:
        if content_type == 'multipart/form-data' and 'boundary' in options:
            parser = MultipartParser(self.rfile,
                                     boundary=options['boundary'],
                                     content_length=content_length)
            for part in parser:
                if self.validate_file(part):
                    unique_name = str(uuid4())[:8]
                    logger.info(f'{part.filename}: File upload ({part.size} bytes)')
                    ext = Path(part.filename).suffix
                    uploaded_name = f'{unique_name}{ext}'
                    part.save_as(MEDIA_PATH / uploaded_name)
                    image_data={
                        'filename': unique_name,
                        'original_name': part.filename,
                        'size': part.size // 1024,
                        'file_type': ext.lstrip('.'),
                    }
                    return image_data

                else:
                    logger.info(
                        f'{part.name}: Invalid file ({part.size} bytes)')
                    return None

            for part in parser.parts():
                part.close()
        return None

    def upload_file(self) -> dict | None:
        content_type, options = parse_options_header(
            self.headers['Content-Type'])
        content_length = int(self.headers['Content-Length'])
        return self.parse_multipart(content_type, options, content_length)
