import datetime
import struct
from typing import List

from .sxf_object import SXFObject


class SXF:

    def __init__(self, path: str):
        self.path = path

        map_file = open(self.path, 'rb')

        raw_passport_data = map_file.read(400)
        self.__parse_passport(raw_passport_data)

        raw_descriptor_data = map_file.read(52)
        self.__parse_descriptor(raw_descriptor_data)

        map_file.close()

    def __parse_passport(self, data: bytes):
        """
        Парсинг паспортных данных.
        """

        # идентификатор файла
        raw_file_id = data[:4]
        self.file_id = struct.unpack('<4s', raw_file_id)[0]
        if self.file_id != b'SXF\x00':
            raise TypeError('Invalid file type!')

        # длина записи паспорта
        raw_passport_len = data[4:8]
        self.passport_len = struct.unpack('<I', raw_passport_len)[0]

        # редакция формата
        raw_version = data[8:12]
        version = struct.unpack('>I', raw_version)[0]
        if version == 0x0400:
            self.version = version
        else:
            raise ValueError('Invalid SXF version!')

        # контрольная сумма
        raw_checksum = data[12:16]
        self.checksum = struct.unpack('<4s', raw_checksum)[0]

        # дата создания набора данных
        raw_date = data[16:28]
        year, month, day = struct.unpack('<4s2s2s4s', raw_date)[:3]
        self.date = datetime.date(int(year), int(month), int(day))

        # номенклатура листа
        raw_nomenclature = data[28:60]
        nomenclature = struct.unpack('<32s', raw_nomenclature)[0]
        self.nomenclature = nomenclature.rstrip(b'\x00')

        # масштаб листа
        raw_scale = data[60:64]
        self.scale = struct.unpack('<I', raw_scale)[0]

        # условное название листа
        raw_name = data[64:96]
        name = struct.unpack('<32s', raw_name)[0]
        self.name = name.rstrip(b'\x00')

        # TODO: информационные флажки

        # код ESPG для системы
        raw_espg = data[100:104]
        self.espg = struct.unpack('<I', raw_espg)[0]

        # прямоугольные координаты углов листа (в метрах)
        raw_rect_coords = data[104:168]
        self.rect_coords = struct.unpack('<dddddddd', raw_rect_coords)

        # геодезические координаты углов листа (в радианах)
        raw_geo_coords = data[168:232]
        self.geo_coords = struct.unpack('<dddddddd', raw_geo_coords)

        # математическая основа листа
        raw_math_base = data[232:240]
        self.math_base = struct.unpack('<BBBBBBBB', raw_math_base)

        # справочные данные об исходном материале
        raw_src_info = data[240:304]
        self.src_info = struct.unpack('<12sBBBBddd12sId', raw_src_info)

        # угол разворота осей для местных систем координат (в радианах по часовой стрелке)
        raw_axes_angle = data[304:312]
        self.axes_angle = struct.unpack('<d', raw_axes_angle)[0]

        # разрешающая способность прибора (точек на метр)
        raw_dpi = data[312:316]
        self.dpi = struct.unpack('<i', raw_dpi)[0]

        # расположение рамки на приборе
        raw_border = data[316:348]
        self.border = struct.unpack('<IIIIIIII', raw_border)

        # классификационный код рамки листа карты
        raw_border_class_code = data[348:352]
        self.border_class_code = struct.unpack('<I', raw_border_class_code)[0]

        # справочные данные о проекции исходного материала
        raw_src_proj_info = data[352:]
        self.src_proj_info = struct.unpack('<dddddd', raw_src_proj_info)

    def __parse_descriptor(self, data):
        """
        Парсинг дескриптора данных.
        """

        # идентификатор данных
        raw_data_id = data[:4]
        self.data_id = struct.unpack('<4s', raw_data_id)[0]
        if self.data_id != b'DAT\x00':
            raise TypeError('Invalid descriptor type!')

        # длина дескриптора
        raw_descriptor_len = data[4:8]
        self.descriptor_len = struct.unpack('<I', raw_descriptor_len)[0]

        # номенклатура листа
        raw_desc_nomenclature = data[8:40]
        desc_nomenclature = struct.unpack('<32s', raw_desc_nomenclature)[0]
        self.desc_nomenclature = desc_nomenclature.rstrip(b'\x00')

        # число записей данных
        raw_records_count = data[40:44]
        self.records_count = struct.unpack('<I', raw_records_count)[0]

        # TODO: информационные флажки

    def __str__(self) -> str:
        return '\n'.join([
            f'Passport length: {self.passport_len}',
            f'SXF version: 0x{self.version:x}',
            f'Creation date: {self.date}',
            f'Nomenclature: {self.nomenclature}',
            f'Scale: 1:{self.scale}',
            f'Name: {self.name}',
            f'ESPG: {self.espg}',
            f'Records count: {self.records_count}'
        ])

    def parse(self) -> List[SXFObject]:
        """
        Парсинг записей, метрик и семантик.
        """

        # заголовок записи
        # матрика объекта и подобъектов
        # семантика объекта

        map_file = open(self.path, 'rb')
        map_file.seek(self.passport_len + self.descriptor_len)

        self.objects = []

        for _ in range(self.records_count):
            self.objects.append(SXFObject(map_file))

        map_file.close()

        return self.objects
