import logging

from psycopg import DatabaseError

from app.settings import MEDIA_PATH
from .base_handler import BaseHandler
from .db_manager import DBManager

logger = logging.getLogger(__name__)


class ImageHostingHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        self.db: DBManager = DBManager()
        super().__init__(*args, **kwargs)


    def do_GET(self):

        logger.info(f'GET {self.client_address[0]}:{self.path}')

        if self.path.startswith('/api'):
            if self.path == '/api/images':
                self.get_images_names()
            elif self.path == '/api/images-data/':  # GET ALL DATA from DataBase about images
                self.get_images()  # GET ALL DATA from DataBase about images
            elif self.path.startswith('/api/images/'):
                name = self.path.split('/')[-1]
                self.send_media_file(name)

        elif self.path == '/':
            self.template_response('index.html')
        elif self.path == '/upload':
            self.template_response('upload.html')
        elif self.path == '/images':
            self.template_response('images.html')
        # Images_List
        # elif any((self.path.endswith(ext) for ext in ['.css', '.js', '.png'])):
        #     self.send_static_file(self.path)
        else:
            self.html_response('Not Found', 404)

    def do_POST(self):

        logger.info(f'POST {self.client_address[0]}:{self.path}')
        if self.path == '/api/upload':
            image_dict = self.upload_file()
            if image_dict:
                self.db.add_image(image_dict)  # SAVE to DataBase
                self.json_response({
                    'message': 'File uploaded successfully',
                    'image': image_dict,
                }, 201)
            else:
                self.json_response({
                    'message': 'Invalid file type or size',
                }, 400)
        else:
            self.html_response('Not Found', 404)

    def do_DELETE(self):

        logger.info(f"DELETE {self.client_address[0]}: {self.path}")
        if self.path.startswith('/api/images/'):
            name = self.path.split('/')[-1]
            name, file_type = name.rsplit('.', 1)
            self.delete_image(name, file_type)

    def get_images_names(self):
        # GET names from DataBase
        self.json_response({
            'images': self.db.get_images_names()}
        )

    def get_images(self):
        images = self.db.get_images()
        res_images = []
        for image in images:
            res_images.append({
                'id': image[0],
                'filename': image[1],
                'original_name': image[2],
                'size': image[3],
                'upload_time': image[4].strftime("%Y/%m/%d %H:%M:%S"),
                'file_type': image[5],
            })
        self.json_response({
            'images': res_images
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
