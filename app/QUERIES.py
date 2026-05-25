CREATE_TABLE = '''CREATE TABLE IF NOT EXISTS images (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Уникальный идентификатор записи
    filename TEXT NOT NULL,              -- Уникальное имя файла (сгенерированное)
    original_name TEXT NOT NULL,         -- Оригинальное имя файла (пользователя)
    size INTEGER NOT NULL,               -- Размер файла в байтах
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Время загрузки файла
    file_type TEXT NOT NULL              -- Формат файла (jpg, png, gif и т.д.)
);'''


ADD_IMAGE = '''
INSERT INTO images (filename, original_name, size, file_type)
    VALUES (%(filename)s, %(original_name)s, %(size)s, %(file_type)s)
'''

DELETE_IMAGE_BY_NAME = '''
DELETE FROM images
WHERE filename = %s
'''

GET_ALL_IMAGES = '''
SELECT * FROM images
'''

GET_IMAGES_NAMES = '''
SELECT filename FROM images
'''

