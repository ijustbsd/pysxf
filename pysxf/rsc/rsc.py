import datetime
import logging
import struct
from typing import BinaryIO, Dict, List, Optional, Tuple

from .primitives import GparhicPrimitive, code_to_primitive
from .rsc_object import RSCObject


class RSC:

    file_id: bytes
    file_len: int
    version: int
    encoding: str
    state_number: int
    correction_number: int
    language: str
    max_id: int
    creation_date: datetime.date
    map_type: str
    name: str
    code: str
    scale: int
    scale_row: int

    obj_offset: int
    obj_len: int
    obj_count: int

    sem_offset: int
    sem_len: int
    sem_count: int

    cls_offset: int
    cls_len: int
    cls_count: int

    def_offset: int
    def_len: int
    def_count: int

    pos_offset: int
    pos_len: int
    pos_count: int

    seg_offset: int
    seg_len: int
    seg_count: int

    lim_offset: int
    lim_len: int
    lim_count: int

    par_offset: int
    par_len: int
    par_count: int

    prn_offset: int
    prn_len: int
    prn_count: int

    pal_offset: int
    pal_len: int
    pal_count: int

    txt_offset: int
    txt_len: int
    txt_count: int

    iml_offset: int
    iml_len: int
    iml_count: int

    img_offset: int
    img_len: int
    img_count: int

    tab_offset: int
    tab_len: int
    tab_count: int

    key_as_code: bool
    palette_mod: bool

    fonts_encoding: int
    palette_colors: int

    # объекты
    objects: Dict[int, List[RSCObject]] = {}

    # палитра
    palette: List[Tuple[int, int, int]] = []
    palette_name: str

    # параметры экрана
    display_params: Dict[int, GparhicPrimitive] = {}

    def __init__(self, path: str):
        self.path = path

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.rsc_file = open(self.path, 'rb')

        self.__parse_header()

        self.rsc_file.close()

    def __parse_header(self):
        """
        Парсинг заголовка.
        """

        # идентификатор файла
        raw_file_id = self.rsc_file.read(4)
        self.file_id = struct.unpack('<4s', raw_file_id)[0]
        if self.file_id != b'RSC\x00':
            raise TypeError('Invalid file type!')

        # длина файла
        raw_len = self.rsc_file.read(4)
        self.len = struct.unpack('<I', raw_len)[0]

        # версия структуры RSC
        raw_version = self.rsc_file.read(4)
        self.version = struct.unpack('<I', raw_version)[0]

        # кодировка
        raw_encoding = self.rsc_file.read(4)
        encoding = struct.unpack('<4s', raw_encoding)[0]
        self.encoding = encoding.rstrip(b'\x00').decode()

        # номер состояния файла
        raw_state_number = self.rsc_file.read(4)
        self.state_number = struct.unpack('<I', raw_state_number)[0]

        # номер модификации состояния
        raw_correction_number = self.rsc_file.read(4)
        self.correction_number = struct.unpack('<I', raw_correction_number)[0]

        # используемый язык
        raw_language = self.rsc_file.read(4)
        language = struct.unpack('<I', raw_language)[0]
        try:
            self.language = {
                1: 'english',
                2: 'russian'
            }[language]
        except KeyError:
            self.logger.warning('Invalid language code!')

        # максимальный идентификатор таблицы объектов
        raw_max_id = self.rsc_file.read(4)
        self.max_id = struct.unpack('<I', raw_max_id)[0]

        # дата создания файла
        raw_creation_date = self.rsc_file.read(8)
        year, month, day = struct.unpack('<4s2s2s', raw_creation_date)[:3]
        self.creation_date = datetime.date(int(year), int(month), int(day))

        # тип карты
        raw_map_type = self.rsc_file.read(32)
        map_type = struct.unpack('<32s', raw_map_type)[0]
        self.map_type = map_type.decode('cp1251')

        # условное название классификатора
        raw_name = self.rsc_file.read(32)
        name = struct.unpack('<32s', raw_name)[0]
        self.name = name.decode('cp1251')

        # код классификатора
        raw_code = self.rsc_file.read(8)
        code = struct.unpack('<8s', raw_code)[0]
        self.code = code.decode('cp1251')

        # масштаб карты
        raw_scale = self.rsc_file.read(4)
        self.scale = struct.unpack('<I', raw_scale)[0]

        # масштабный ряд
        raw_scale_row = self.rsc_file.read(4)
        self.scale_row = struct.unpack('<I', raw_scale_row)[0]

        # смещение на таблицу объектов
        raw_obj_offset = self.rsc_file.read(4)
        self.obj_offset = struct.unpack('<I', raw_obj_offset)[0]

        # длина таблицы объектов
        raw_obj_len = self.rsc_file.read(4)
        self.obj_len = struct.unpack('<I', raw_obj_len)[0]

        # число записей
        raw_obj_count = self.rsc_file.read(4)
        self.obj_count = struct.unpack('<I', raw_obj_count)[0]

        cur_pos = self.rsc_file.tell()
        self.rsc_file.seek(cur_pos + 18 * 4)

        # смещение на таблицу параметров
        raw_par_offset = self.rsc_file.read(4)
        self.par_offset = struct.unpack('<I', raw_par_offset)[0]

        # длина таблицы параметров
        raw_par_len = self.rsc_file.read(4)
        self.par_len = struct.unpack('<I', raw_par_len)[0]

        # число записей
        raw_par_count = self.rsc_file.read(4)
        self.par_count = struct.unpack('<I', raw_par_count)[0]

        # смещение на таблицу параметров печати
        raw_prn_offset = self.rsc_file.read(4)
        self.prn_offset = struct.unpack('<I', raw_prn_offset)[0]

        # длина таблицы параметров печати
        raw_prn_len = self.rsc_file.read(4)
        self.prn_len = struct.unpack('<I', raw_prn_len)[0]

        # число записей
        raw_prn_count = self.rsc_file.read(4)
        self.prn_count = struct.unpack('<I', raw_prn_count)[0]

        # смещение на таблицу параметров печати
        raw_pal_offset = self.rsc_file.read(4)
        self.pal_offset = struct.unpack('<I', raw_pal_offset)[0]

        # длина таблицы параметров печати
        raw_pal_len = self.rsc_file.read(4)
        self.pal_len = struct.unpack('<I', raw_pal_len)[0]

        # число записей
        raw_pal_count = self.rsc_file.read(4)
        self.pal_count = struct.unpack('<I', raw_pal_count)[0]

    def __str__(self) -> str:
        return '\n'.join([
            f'Length: {self.len}',
            f'Version: 0x{self.version:x}',
            f'Encoding: {self.encoding}',
            f'State number: {self.state_number}',
            f'Correction number: {self.correction_number}',
            f'Language: {self.language}',
            f'Maximum object ID: {self.max_id}',
            f'Creation date: {self.creation_date}',
            f'Map type: {self.map_type}',
            f'Name: {self.name}',
            f'Code: {self.code}',
            f'Scale: {self.scale}',
            f'Scale row: {self.scale_row}'
        ])

    def __get_table_row(self,
                        fp: BinaryIO,
                        length: int,
                        format: str,
                        index: Optional[int] = None):
        raw_data = fp.read(length)
        result = struct.unpack(format, raw_data)
        if index is not None:
            return result[index]
        return result

    def parse_objects(self):
        """
        Парсинг таблицы объектов.
        """

        rsc_file = open(self.path, 'rb')
        rsc_file.seek(self.obj_offset - 4)

        raw_obj_id = rsc_file.read(4)
        obj_id = struct.unpack('<4s', raw_obj_id)[0]
        if obj_id != b'OBJ\x00':
            raise ValueError('Invalid OBJ table ID!', obj_id)

        for _ in range(self.obj_count):
            rsc_obj = RSCObject(rsc_file)
            if rsc_obj.class_code in self.objects:
                self.objects[rsc_obj.class_code].append(rsc_obj)
            else:
                self.objects[rsc_obj.class_code] = [rsc_obj]

        rsc_file.close()

    def parse_display_params(self):
        """
        Парсинг таблицы параметров экрана.
        """

        rsc_file = open(self.path, 'rb')
        rsc_file.seek(self.par_offset - 4)

        raw_par_id = rsc_file.read(4)
        par_id = struct.unpack('<4s', raw_par_id)[0]
        if par_id != b'PAR\x00':
            raise ValueError('Invalid PAR table ID!')

        par_template = {
            'len': (4, '<I'),
            'internal_code': (2, '<H'),
            'show_code': (2, '<H'),
        }

        for _ in range(self.par_count):

            par = {}
            for k, v in par_template.items():
                par[k] = self.__get_table_row(rsc_file, *v, 0)

            data_len = par['len'] - 8
            par['raw_data'] = self.__get_table_row(rsc_file, data_len, f'<{data_len}s', 0)

            primitive = code_to_primitive(par['show_code'])
            if primitive is not None:
                prim = primitive(par['raw_data'])
                prim.parse()

                # if prim.color is not None:
                #     is_rgb, *data = prim.color
                #     if is_rgb == 0xF0:
                #         prim.color = self.palette[data[-1]]
                #     else:
                #         prim.color = data

                self.display_params[par['internal_code']] = prim

        rsc_file.close()

    def parse_palette(self):
        rsc_file = open(self.path, 'rb')
        rsc_file.seek(self.pal_offset - 4)

        raw_pal_id = rsc_file.read(4)
        pal_id = struct.unpack('<4s', raw_pal_id)[0]
        if pal_id != b'PAL\x00':
            raise ValueError('Invalid PAL table ID!')

        for _ in range(self.pal_count * 256):
            rgb = self.__get_table_row(rsc_file, 4, '<BBBB')[:3]
            self.palette.append(rgb)

        name = self.__get_table_row(rsc_file, 32, '<32s', 0)
        self.palette_name = name.decode('cp1251')

        rsc_file.close()
