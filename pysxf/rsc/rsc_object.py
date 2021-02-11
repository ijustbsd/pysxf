import struct
from typing import BinaryIO


class RSCObject:

    length: int
    class_code: int
    internal_code: int
    id: int
    name: str
    title: str

    def __init__(self, fp: BinaryIO):
        self.fp = fp

        # длина записи объекта
        raw_len = self.fp.read(4)
        self.length = struct.unpack('<I', raw_len)[0]

        # классификационный код
        raw_class_code = self.fp.read(4)
        self.class_code = struct.unpack('<I', raw_class_code)[0]

        # внутренний код
        raw_internal_code = self.fp.read(4)
        self.internal_code = struct.unpack('<I', raw_internal_code)[0]

        # идентификационный код
        raw_id = self.fp.read(4)
        self.id = struct.unpack('<I', raw_id)[0]

        # короткое имя объекта
        raw_name = self.fp.read(32)
        self.name = struct.unpack('<32s', raw_name)[0]

        # название
        raw_title = self.fp.read(32)
        self.title = struct.unpack('<32s', raw_title)[0]

        # характер локализации
        raw_type = self.fp.read(1)
        self.type = struct.unpack('<B', raw_type)[0]

        self.fp.read(self.length - 81)

    def __str__(self):
        return '\n'.join([
            f'Length: {self.length}',
            f'Classification code: {self.class_code}',
            f'Internal code: {self.internal_code}',
            f'ID: {self.id}',
            f'Name: {self.name}',
            f'Title: {self.title}'
        ])
