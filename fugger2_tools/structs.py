from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield


@dataclass
class Icon3RowData(DataclassMixin):
    count_transparent: int = csfield(cs.Int8ul)
    count: int = csfield(cs.Int8ul)
    pixels: list[int] = csfield(cs.Array(lambda ctx: ctx.count, cs.Int16ul))

    next_value: int = csfield(cs.Peek(cs.Int8ul))
    const_fe: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFE, cs.Int8ul))
    const_ff: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFF, cs.Int8ul))


@dataclass
class Icon3EightBitRowData(DataclassMixin):
    count_transparent: int = csfield(cs.Int8ul)
    count: int = csfield(cs.Int8ul)
    pixels: list[int] = csfield(cs.Array(lambda ctx: ctx.count, cs.Int8ul))

    next_value: int = csfield(cs.Peek(cs.Int8ul))
    const_fe: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFE, cs.Int8ul))
    const_ff: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFF, cs.Int8ul))


@dataclass
class Icon3Row(DataclassMixin):
    next_value: int = csfield(cs.Peek(cs.Int8ul))
    const_fe: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFE, cs.Int8ul))
    const_ff: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFF, cs.Int8ul))

    data: Icon3RowData | None = csfield(
        cs.If(
            lambda ctx: ctx.const_fe is None and ctx.const_ff is None,
            DataclassStruct(Icon3RowData),
        )
    )


@dataclass
class Icon3EightBitRow(DataclassMixin):
    next_value: int = csfield(cs.Peek(cs.Int8ul))
    const_fe: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFE, cs.Int8ul))
    const_ff: int | None = csfield(cs.If(lambda ctx: ctx.next_value == 0xFF, cs.Int8ul))

    data: Icon3EightBitRowData | None = csfield(
        cs.If(
            lambda ctx: ctx.const_fe is None and ctx.const_ff is None,
            DataclassStruct(Icon3EightBitRowData),
        )
    )


@dataclass
class Icon3(DataclassMixin):
    rows: list[Icon3Row] = csfield(
        cs.RepeatUntil(
            lambda obj, arr, ctx: not ctx._io.peek(1),  # type: ignore
            DataclassStruct(Icon3Row),
        )
    )


@dataclass
class Icon3Write(DataclassMixin):
    rows: list[Icon3Row] = csfield(cs.GreedyRange(DataclassStruct(Icon3Row)))


@dataclass
class Icon3EightBit(DataclassMixin):
    rows: list[Icon3EightBitRow] = csfield(
        cs.RepeatUntil(
            lambda obj, arr, ctx: not ctx._io.peek(1),  # type: ignore
            DataclassStruct(Icon3EightBitRow),
        )
    )


@dataclass
class IconGeneral(DataclassMixin):
    width: int = csfield(cs.Int16ul)
    height: int = csfield(cs.Int16ul)
    pixels: list[int] = csfield(
        cs.Array(lambda ctx: ctx.width * ctx.height, cs.Int16ul)
    )


@dataclass
class IconIN(DataclassMixin):
    pixels: list[int] = csfield(cs.Array(256 * 9, cs.Int16ul))


@dataclass
class Icon3WithHeader(DataclassMixin):
    header_length: int = csfield(cs.Peek(cs.Int8ul))
    header: bytes = csfield(cs.Bytes(lambda ctx: ctx.header_length))
    icon: Icon3EightBit = csfield(DataclassStruct(Icon3EightBit))
