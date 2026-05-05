from __future__ import annotations

import logging
from http.server import BaseHTTPRequestHandler
import multipart
from app.settings import STATIC_DIR, MEDIA_DIR

logger = logging.getLogger(__name__)


class BaseHandler(BaseHTTPRequestHandler):
    server_version = '0.1'
    server_name = 'Image Hosting Server'

    def response (self,data: str | bytes,content_type: str='text/html', status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(data if isinstance(data, bytes) else data.encode('utf-8'))

    def html_response(self, data:str | bytes, status_code=200)->None:
        self.response(data, 'text/html', status_code)

    @staticmethod
    def load_static(filename:str)->bytes:
        try:
            with open(f'../{STATIC_DIR}/{filename}', 'rb') as file:
                return file.read()
        except FileNotFoundError:
            return b'Not Found'

    def template_response(self, template_filename: str) -> None:
        self.html_response(self.load_static(template_filename))

    def send_file(self,filename:str)->None:
        if filename.endswith('.png'):
            content_type='image/png'
        elif filename.endswith('.css'):
            content_type='text/css'
        elif filename.endswith('.js'):
            content_type='text/javascript'
        else:
            content_type='application/octet-stream'
        self.response(self.load_static(filename), content_type)


    def parse_multipart(self, content_type: str, options:dict, content_length:int, filename:str = None)-> None:

        if content_type == 'multipart/form-data' and 'boundary' in options:
            parser = multipart.MultipartParser(self.rfile,
                                               boundary=options['boundary'],
                                               content_length=content_length)

            for part in parser:
                if part.filename:
                    logger.info(f'{part.name}: File upload ({part.size} bytes)')
                    part.save_as(f'../{MEDIA_DIR}/{filename or part.filename}')

            for part in parser.parts():
                part.close()
        self.response('Got your file', 'text/plain')

    def upload_file(self, filename:str=None) -> None:
        content_type, options = multipart.parse_options_header(
            self.headers['Content-Type'])
        content_length = int(self.headers['Content-Length'])
        self.parse_multipart(content_type, options, content_length, filename)

