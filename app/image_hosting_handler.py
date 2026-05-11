import logging
import uuid
from enum import unique

from base_handler import BaseHandler
import multipart

logger = logging.getLogger(__name__)

class ImageHostingHandler(BaseHandler):


    def do_GET(self):
        logger.info(f'GET {self.client_address[0]}:{self.path}')
        if self.path == '/':
            self.template_response('index.html')
        elif self.path == '/upload':
            self.template_response('upload.html')
        elif self.path == '/images':
            self.template_response('images.html')
        elif any((self.path.endswith(ext) for ext in ['.css', '.js', '.png'])):
            self.send_file(self.path)
        else:
            self.html_response('Not Found', 400)

    def do_POST(self):
        logger.info(f'POST {self.client_address[0]}:{self.path}')
        if self.path == '/api/upload':
            unique_id = uuid.uuid4()
            self.upload_file(str(unique_id)[:8])
        else:
            self.html_response('Not Found', 400)





