import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

WORKDIR = pathlib.Path().cwd().parent.resolve()

STATIC_DIR=os.getenv('STATIC_DIR','static')
STATIC_PATH=WORKDIR/STATIC_DIR

MEDIA_DIR = os.getenv('MEDIA_DIR', 'images')
MEDIA_PATH = WORKDIR/MEDIA_DIR
