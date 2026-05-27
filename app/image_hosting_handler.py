from urllib.parse import urlsplit

import logging

from psycopg import DatabaseError

from app.base_handler import BaseHandler
from app.db_manager import DBManager
from app.settings import MEDIA_PATH

logger = logging.getLogger(__name__)


class ImageHostingHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        self.db: DBManager = DBManager()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        logger.info(f"GET {self.client_address[0]}: {self.path}")

        if self.path == '/':
            self.template_response('index.html')
        elif self.path == '/upload':
            self.template_response('upload.html')
        elif self.path.startswith('/images'):
            self.template_response('images.html')
        elif self.path.startswith('/api/images-data'):
            path = urlsplit(self.path)
            page = int(path.query.split('=')[1]) if path.query else 1
            self.get_images(page)
        elif self.path.startswith('/api/images'):
            self.get_images_names()
        else:
            self.html_response('Not Found', 404)

    def do_POST(self):
        logger.info(f"POST {self.client_address[0]}: {self.path}")
        if self.path == '/api/upload':
            image_dict = self.upload_file()
            if image_dict:
                self.db.add_image(image_dict)
                self.json_response({
                    'message': 'File uploaded successfully',
                    'image': image_dict
                }, 201)
            else:
                self.json_response({
                    'message': 'Invalid file type or file size'
                }, 400)
        else:
            self.html_response('Not Found', 404)

    def do_DELETE(self):

        logger.info(f"DELETE {self.client_address[0]}: {self.path}")
        if self.path.startswith('/api/images/'):
            name = self.path.split('/')[-1]
            name, file_type = name.rsplit('.', 1)
            self.delete_image(name, file_type)

    def get_images_names(self, *args):
        self.json_response({
            'images': self.db.get_images_names()}
        )

    def get_images(self, page: int):
        images = self.db.get_images(page)
        # images = images or []
        has_next = self.db.has_next(page)
        res_images = [
            {
                'id': i[0],
                'filename': i[1],
                'original_name': i[2],
                'size': i[3],
                'upload_time': i[4].strftime('%Y-%m-%d %H:%M:%S'),
                'file_type': i[5]
            }
            for i in images
        ]
        self.json_response({
            'images': res_images,
            'has_next': has_next
        })

    def delete_image(self, name: str, file_type: str):
        try:
            self.db.delete_image(name)
            (MEDIA_PATH / (name + '.' + file_type)).unlink()
            logger.info(f"Image {name} deleted successfully")
            self.json_response({'message': 'Image deleted successfully'},
                               status_code=204)
        except FileNotFoundError:
            logger.info(f"File {name} not found (on delete)")
            self.json_response({'message': 'Image not found'}, 404)
        except DatabaseError:
            logger.info(f"{name} not found in database (on delete)")
            self.json_response({'message': 'Image not found'}, 404)