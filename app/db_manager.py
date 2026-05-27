import os
from math import ceil
from typing import Optional, Any

import logging
from dotenv import load_dotenv
from psycopg import Connection, connect, ProgrammingError, OperationalError
from psycopg.abc import Params
from psycopg.rows import tuple_row

from app.QUERIES import ADD_IMAGE, GET_IMAGES_NAMES, DELETE_IMAGE_BY_NAME, \
    GET_ALL_IMAGES, CREATE_TABLE, GET_IMAGES_COUNT
from app.settings import IMAGE_LIMIT

load_dotenv()
DB = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'dbname': os.getenv('POSTGRES_DB'),
}

DSN = f"postgresql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['dbname']}"
logger = logging.getLogger(__name__)


class DBManager:
    def __init__(self, db_config: dict = None, row_factory=tuple_row):
        self.db_config = db_config or DB
        self.dsn = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['dbname']}"
        self._connection: Optional[Connection] = None
        self.row_factory = row_factory

        # self.init_tables()

    def _execute(self, query, data: Params = None, fetch: bool = True,
                 fetch_all: bool = True) -> list | None:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, data)
                    if fetch:
                        result = cur.fetchall() if fetch_all else cur.fetchone()
                        return result
            self._connection = None

        except OperationalError as e:
            print(f"Не удалось подключиться к базе данных:\n{e}")

        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе:\n{e}")


    def _connect(self) -> Optional[Connection]:
        return self._connection if self._connection else connect(self.dsn,
                                                                 row_factory=self.row_factory)

    def fetch_all(self, query, data: Params = None) -> list | None:
        return self._execute(query, data)

    def fetch_one(self, query, data: Params = None) -> Any:
        return self._execute(query, data, fetch_all=False)[0]

    def execute(self, query, data: Params = None) -> list | None:
        return self._execute(query, data, fetch=False, fetch_all=False)

    def add_image(self, image: dict):
        self.execute(ADD_IMAGE, image)

    def get_images_names(self):
        return self.fetch_all(GET_IMAGES_NAMES)

    def get_images(self, page: int):
        offset = (page - 1) * IMAGE_LIMIT
        logger.info(f"offset: {offset}")
        return self.fetch_all(GET_ALL_IMAGES, (offset,))

    def delete_image(self, name):
        self.execute(DELETE_IMAGE_BY_NAME, (name,))

    def init_tables(self):
        self.execute(CREATE_TABLE)

    def has_next(self, page):
        images_count = self.fetch_one(GET_IMAGES_COUNT)
        return ceil(images_count / IMAGE_LIMIT) > page