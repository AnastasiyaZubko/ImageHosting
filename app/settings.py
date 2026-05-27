import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

# WORKDIR = pathlib.Path().cwd().parent.resolve()
WORKDIR = pathlib.Path(__file__).parent.parent.resolve()

STATIC_DIR = os.getenv('STATIC_DIR', 'static')
STATIC_PATH = WORKDIR / STATIC_DIR

MEDIA_DIR = os.getenv('MEDIA_DIR', 'images')
MEDIA_PATH = WORKDIR / MEDIA_DIR

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

LOGDIR = os.getenv('LOGDIR', 'logs')
LOG_PATH = WORKDIR / LOGDIR

MEDIA_PATH.mkdir(parents=True, exist_ok=True)
LOG_PATH.mkdir(parents=True, exist_ok=True)

IMAGE_LIMIT = int(os.getenv('IMAGES_LIMIT', 5))