import struct
from enum import IntEnum
from typing import BinaryIO


class ObjectType(IntEnum):
    LINE = 0
    AREA = 1
    POINT = 2
    LABEL = 3
    VECTOR = 4
    TEMPLATE = 5


class SXFObject:

    def __init__(self, data: BinaryIO):
        self.raw_data = data

        self.__parse_header()
        self.__parse_metrics()
        if self.has_text:
            self.__parse_text()
        if self.subitems_count:
            if self.type in (ObjectType.LABEL, ObjectType.TEMPLATE):
                self.__parse_text_subitems()
            else:
                self.__parse_subitems()
        if self.has_graphics:
            self.__parse_graphics()
        # TODO: парсинг вектора привзяки 3D-моедли объекта
        if self.has_semantics:
            self.__parse_semantics()

    def __str__(self):
        return '\n'.join([
            f'Start ID: 0x{self.start_id:x}',
            f'Full length: {self.full_len}',
            f'Metrics length: {self.metrics_len}',
            f'Classifier code: {self.classifier_code}',
            f'ID: {self.id}',
            f'Group ID: {self.group_id}',
            f'Generalization level: {self.general_levels}',
            f'Big objects points count: {self.big_points_count}',
            f'Subitems count: {self.subitems_count}',
            f'Points count: {self.points_count}',
            f'Text: {self.text if self.has_text else None}',
            f'Has graphics: {self.has_graphics}',
            f'Has semantics: {self.has_semantics}'
        ])

    def __parse_header(self):
        """
        Парсинг заголовка объекта.
        """

        data = self.raw_data.read(32)

        # идентификатор начала записи
        raw_start_id = data[:4]
        self.start_id = struct.unpack('>I', raw_start_id)[0]
        if self.start_id != 0xFF7FFF7F:
            raise ValueError('Invalid SXF object!')

        # общая длина записи
        raw_full_len = data[4:8]
        self.full_len = struct.unpack('<I', raw_full_len)[0]

        # длина метрики (в байтах)
        raw_metrics_len = data[8:12]
        self.metrics_len = struct.unpack('<I', raw_metrics_len)[0]

        # классификационный код
        raw_classifier_code = data[12:16]
        self.classifier_code = struct.unpack('<I', raw_classifier_code)[0]

        # собственный номер объекта
        raw_id = data[16:20]
        self.id, self.group_id = struct.unpack('<HH', raw_id)

        # TODO: справочные данные
        raw_help_data = data[20:23]
        help_data = struct.unpack('<BBB', raw_help_data)
        self.type = help_data[0] & 0x0F
        self.has_semantics = bool(help_data[1] & 2)
        self.raw_data_size = bool(help_data[1] & 4)
        self.raw_data_type = bool(help_data[2] & 4)
        self.has_text = bool(help_data[2] & 8)
        self.has_graphics = bool(help_data[2] & 16)

        try:
            self.data_size, self.data_type = {
                (0, 0): (2, '<H'),
                (0, 1): (4, '<f'),
                (1, 0): (4, '<i'),
                (1, 1): (8, '<q')
            }[(self.raw_data_size, self.raw_data_type)]
        except KeyError:
            raise ValueError('Invalid metrics coordinates format!')

        # уровень генерализации
        raw_general_levels = data[23:24]
        raw_levels = struct.unpack('<B', raw_general_levels)[0]
        self.general_levels = (raw_levels >> 4, raw_levels & 0x0F)

        # число точек метрики для больших объектов
        raw_big_points_count = data[24:28]
        self.big_points_count = struct.unpack('<I', raw_big_points_count)

        # описатель метрики
        raw_metrics_count = data[28:32]
        self.subitems_count, self.points_count = struct.unpack('<HH', raw_metrics_count)

    def __parse_metrics(self):
        """
        Парсинг метрики объекта.
        """

        self.points = []
        for i in range(self.points_count):
            x = struct.unpack(self.data_type, self.raw_data.read(self.data_size))[0]
            y = struct.unpack(self.data_type, self.raw_data.read(self.data_size))[0]
            self.points.append((x, y))

    def __parse_subitems(self):
        """
        Парсинг подобъектов.
        """

        self.subitems = []

        for _ in range(self.subitems_count):
            points = []
            raw_n_data = self.raw_data.read(4)
            n1, n2 = struct.unpack('<HH', raw_n_data)

            if self.points_count == 65535:
                points_count = n2 + (n1 << 16)
            else:
                points_count = n2

            for i in range(points_count):
                x = struct.unpack(self.data_type, self.raw_data.read(self.data_size))[0]
                y = struct.unpack(self.data_type, self.raw_data.read(self.data_size))[0]
                points.append((x, y))
            self.subitems.append(points)

    def __parse_text(self):
        """
        Парсинг подписи.
        """

        raw_text_size = self.raw_data.read(1)
        text_size = struct.unpack('<B', raw_text_size)[0]

        raw_text = self.raw_data.read(text_size + 1)
        text = struct.unpack(f'<{text_size + 1}s', raw_text)[0]

        self.text = text.rstrip(b'\x00')

    def __parse_text_subitems(self):
        """
        Парсинг подобъектов объектов типа "подпись".
        """

        self.text_subitems = []

        for _ in range(self.subitems_count):
            points = []
            raw_n_data = self.raw_data.read(4)
            n1, n2 = struct.unpack('<HH', raw_n_data)

            if self.points_count == 65535:
                points_count = n2 + (n1 << 16)
            else:
                points_count = n2

            for i in range(points_count):
                x = struct.unpack(self.data_type, self.raw_data.read(self.data_size))[0]
                y = struct.unpack(self.data_type, self.raw_data.read(self.data_size))[0]
                points.append((x, y))

            raw_text_size = self.raw_data.read(1)
            text_size = struct.unpack('<B', raw_text_size)[0]

            raw_text = self.raw_data.read(text_size + 1)
            text = struct.unpack(f'<{text_size + 1}s', raw_text)[0]
            strip_text = text.rstrip(b'\x00')
            self.text_subitems.append({'points': points, 'text': strip_text})

    def __parse_graphics(self):
        """
        Парсинг графического объекта.
        """

        raise NotImplementedError

    def __parse_semantics(self):
        """
        Парсинг семантики объекта.
        """

        cur_sem_len = self.full_len - self.metrics_len - 32

        self.semantics = {}

        while cur_sem_len > 0:

            # код характеристики
            raw_feature_code = self.raw_data.read(2)
            feature_code = struct.unpack('>H', raw_feature_code)[0]
            cur_sem_len -= 2

            # код длины блока
            raw_block_len = self.raw_data.read(2)
            feature_type, feature_scale = struct.unpack('>Bb', raw_block_len)
            cur_sem_len -= 2

            if feature_type in (0, 126, 127, 128):
                feature_scale &= 0xff
                null_size = 2 if feature_type >= 127 else 1
                raw_feature_value = self.raw_data.read(feature_scale + null_size)
                feature_value = struct.unpack(f'<{feature_scale + null_size}s', raw_feature_value)[0]
                feature_value = feature_value.rstrip(b'\x00')
                cur_sem_len -= (feature_scale + null_size)
            elif feature_type in (1, 2, 4, 8, 16):
                type_ = {
                    1: '<b',
                    2: '<h',
                    4: '<i',
                    8: '<d',
                    16: '<16s'
                }[feature_type]
                raw_feature_value = self.raw_data.read(feature_type)
                feature_value = struct.unpack(type_, raw_feature_value)[0]
                feature_value = feature_value * 10 ** feature_scale
                cur_sem_len -= feature_type
            else:
                raise ValueError('Invalid feature type!')

            self.semantics[feature_code] = feature_value

            # пропускаем "лишние" байты в семантике :/
            if cur_sem_len <= 4:
                self.raw_data.read(cur_sem_len)
                break
