import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

STATIC_DIR=os.getenv('STATIC_DIR','static')
STATIC_PATH=pathlib.Path().cwd().parent.resolve()/STATIC_DIR
