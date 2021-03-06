import struct
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

Color = Tuple[int, int, int, int]


def code_to_primitive(code):
    return {
        128: Line,
        129: DottedLine,
        148: ShiftDottedLine,
        135: Area,
        153: DottedArea,
        143: Point,
        144: PatternArea,
        140: Circle,
        142: Label,
        147: SetPrimitives
    }.get(code)


class GparhicPrimitive(ABC):
    raw_data: bytes
    code: int
    color: Optional[Color] = None

    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data

    def __str__(self) -> str:
        name = self.__class__.__name__
        items = self.__dict__.items()
        return '\n'.join([name + ':'] + [f'> {k}: {v}' for k, v in items])

    @abstractmethod
    def parse(self): ...


class Line(GparhicPrimitive):
    """Простая линия."""
    code = 128
    width: int

    def parse(self):
        self.color = struct.unpack('<BBBB', self.raw_data[:4])[::-1]
        self.width = struct.unpack('<I', self.raw_data[4:8])[0]


class DottedLine(Line):
    """Пунктирная линия."""
    code = 129
    stroke_len: int
    space_len: int

    def parse(self):
        super().parse()
        self.stroke_len = struct.unpack('<I', self.raw_data[8:12])[0]
        self.space_len = struct.unpack('<I', self.raw_data[12:16])[0]


class ShiftDottedLine(DottedLine):
    """Смещённый пунктир."""
    code = 148
    shift: int

    def parse(self):
        super().parse()
        self.shift = struct.unpack('<I', self.raw_data[16:20])[0]


class Area(GparhicPrimitive):
    """Площадь."""
    code = 135

    def parse(self):
        self.color = struct.unpack('<BBBB', self.raw_data[:4])[::-1]


class DottedArea(GparhicPrimitive):
    """Штрихованная площадь."""
    code = 153
    length: int
    stroke_angle: int
    stroke_step: int
    stroke_line_code: int
    stroke_line: GparhicPrimitive

    def parse(self):
        self.length = struct.unpack('<I', self.raw_data[:4])[0]
        self.stroke_angle = struct.unpack('<I', self.raw_data[4:8])[0]
        self.stroke_step = struct.unpack('<I', self.raw_data[8:12])[0]
        self.stroke_line_code = struct.unpack('<I', self.raw_data[12:16])[0]
        line_data = struct.unpack('<I', self.raw_data[16:self.length-16])[0]
        line_primitive = code_to_primitive(self.stroke_line_code)
        if line_primitive is not None:
            self.stroke_line = line_primitive(line_data)
            self.stroke_line.parse()


class Point(GparhicPrimitive):
    """Точечный объект."""
    code = 143
    length: int
    mask_count: int
    side_size: int
    vertical_anchor: int
    horizontal_anchor: int
    masks: List[Tuple[Color, Tuple[int]]]

    def parse(self):
        self.masks = []

        self.length = struct.unpack('<I', self.raw_data[:4])[0]
        self.mask_count = struct.unpack('<I', self.raw_data[4:8])[0]
        self.side_size = struct.unpack('<I', self.raw_data[8:12])[0]
        self.vertical_anchor = struct.unpack('<I', self.raw_data[12:16])[0]
        self.horizontal_anchor = struct.unpack('<I', self.raw_data[16:20])[0]

        i = 20
        for _ in range(self.mask_count):
            color = struct.unpack('<BBBB', self.raw_data[i:i+4])[::-1]
            i += 4
            mask = struct.unpack('<128B', self.raw_data[i:i+128])
            mask_bin = tuple(int(bit) for byte in mask for bit in bin(byte)[2:].zfill(8))
            self.masks.append((color, mask_bin))


class PatternArea(GparhicPrimitive):
    """Площадь, заполненная знаками."""
    code = 144
    grid_type: int
    fill_type: bool
    border_width: int
    sign: Point

    def parse(self):
        self.grid_type = struct.unpack('<H', self.raw_data[:2])[0]
        self.fill_type = struct.unpack('<B', self.raw_data[2:3])[0]
        self.border_width = struct.unpack('<B', self.raw_data[3:4])
        self.sign = Point(self.raw_data[4:])
        self.sign.parse()


class Circle(GparhicPrimitive):
    """Окружность."""
    code = 140
    width: int
    radius: int

    def parse(self):
        self.color = struct.unpack('<BBBB', self.raw_data[:4])[::-1]
        self.width = struct.unpack('<I', self.raw_data[4:8])[0]
        self.radius = struct.unpack('<I', self.raw_data[8:12])[0]


class Label(GparhicPrimitive):
    """Текст."""
    code = 142
    background_color: Color
    shadow_color: Color
    height: int
    weight: int
    align: int
    char_width: int
    is_horizontal: bool
    is_italic: bool
    is_underline: bool
    is_strikeout: bool
    type: int
    code_page: bytes
    scale: bool

    def parse(self):
        self.color = struct.unpack('<BBBB', self.raw_data[:4])[::-1]
        self.background_color = struct.unpack('<BBBB', self.raw_data[4:8])[::-1]
        self.shadow_color = struct.unpack('<BBBB', self.raw_data[8:12])[::-1]
        self.height = struct.unpack('<I', self.raw_data[12:16])[0]
        self.weight = struct.unpack('<I', self.raw_data[16:20])[0]
        self.align = struct.unpack('<H', self.raw_data[20:22])[0]
        self.char_width = struct.unpack('<B', self.raw_data[24:25])[0]
        self.is_horizontal = bool(struct.unpack('<B', self.raw_data[25:26])[0])
        self.is_italic = bool(struct.unpack('<B', self.raw_data[26:27])[0])
        self.is_underline = bool(struct.unpack('<B', self.raw_data[27:28])[0])
        self.is_strikeout = bool(struct.unpack('<B', self.raw_data[28:29])[0])
        self.type = struct.unpack('<B', self.raw_data[29:30])[0]
        self.code_page = struct.unpack('<B', self.raw_data[30:31])[0]
        self.scale = bool(struct.unpack('<B', self.raw_data[31:32])[0])


class SetPrimitives(GparhicPrimitive):
    """Набор примитивов."""
    code = 147
    id: bytes
    length: int
    count: int
    primitives: List[GparhicPrimitive]

    def parse(self):
        self.id = struct.unpack('<4s', self.raw_data[:4])
        self.length = struct.unpack('<I', self.raw_data[4:8])[0]
        self.count = struct.unpack('<I', self.raw_data[8:12])[0]

        self.primitives = []

        i = 12
        for _ in range(self.count):
            prim_len = struct.unpack('<H', self.raw_data[i:i+2])[0]
            i += 2
            prim_code = struct.unpack('<H', self.raw_data[i:i+2])[0]
            i += 2
            data_len = prim_len - 4
            prim_data = struct.unpack(f'<{data_len}s', self.raw_data[i:i+data_len])[0]
            i += data_len
            primitive = code_to_primitive(prim_code)
            if primitive is not None:
                prim = primitive(prim_data)
                prim.parse()
                self.primitives.append(prim)
