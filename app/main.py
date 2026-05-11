import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from dotenv import load_dotenv
from app.image_hosting_handler import ImageHostingHandler
import settings
from app.settings import LOG_PATH

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(LOG_PATH / 'server.log')
                    ]
                    )

logger = logging.getLogger(__name__)


def run(server_address = ('',8000),server_class=HTTPServer, handler_class=ImageHostingHandler):

    logger.info(f'Starting Server on {server_address}]')
    httpd = server_class(server_address, handler_class) # noqa

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Server stopped by user')
        httpd.server_close()
    except Exception as error:
        logger.error(f'Error: {error}')

if __name__ == '__main__':
    run()