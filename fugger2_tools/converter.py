from PIL import Image

from fugger2_tools.structs import (
    Icon3,
    Icon3EightBit,
    Icon3Row,
    Icon3RowData,
    Icon3WithHeader,
    Icon3Write,
    IconGeneral,
    IconIN,
)


class Converter:
    def __init__(self) -> None:
        pass

    # def convert_565_to_888(self, color):
    #     # Extract RGB components from 16-bit 565 RGB
    #     red = (color >> 11) & 0x1F
    #     green = (color >> 5) & 0x3F
    #     blue = color & 0x1F

    #     # Scale values to 8-bit range, paying special attention to the green channel
    #     red = (red * 255 + 15) // 31
    #     green = (green * 255 + 31) // 63
    #     blue = (blue * 255 + 15) // 31

    #     return (red, green, blue)

    def convert_555_to_888(self, color: int) -> tuple[int, int, int]:
        red = (color >> 10) & 0x1F
        green = (color >> 5) & 0x1F
        blue = color & 0x1F

        red = (red * 255 + 15) // 31
        green = (green * 255 + 15) // 31
        blue = (blue * 255 + 15) // 31

        return (red, green, blue)

    def convert_332_to_888(self, color: int) -> tuple[int, int, int]:
        red = (color >> 5) & 0x7
        green = (color >> 2) & 0x7
        blue = color & 0x3

        red = (red * 255 + 3) // 7
        green = (green * 255 + 3) // 7
        blue = (blue * 255 + 1) // 3

        return (red, green, blue)

    def convert_icon_general(self, icon_general: IconGeneral) -> Image.Image:
        img = Image.new("RGBA", (icon_general.width, icon_general.height), "black")

        for y in range(icon_general.height):
            for x in range(icon_general.width):
                pixel = icon_general.pixels[y * icon_general.width + x]
                rgb = self.convert_555_to_888(pixel)
                img.putpixel((x, y), (*rgb, 255))

        return img

    def convert_icon_in(self, icon_in: IconIN) -> Image.Image:
        img = Image.new("RGBA", (256, 9), "black")

        for y in range(9):
            for x in range(256):
                pixel = icon_in.pixels[y * 256 + x]
                rgb = self.convert_555_to_888(pixel)
                img.putpixel((x, y), (*rgb, 255))

        return img

    def convert_icon3_with_header(
        self, icon3_with_header: Icon3WithHeader
    ) -> Image.Image | None:
        return self.convert_icon3_eight_bit(icon3_with_header.icon)

    def convert_icon3(self, icon3: Icon3) -> Image.Image | None:
        if len(icon3.rows) == 0 or not any(row.data is not None for row in icon3.rows):
            return None

        actual_rows: list[list[tuple[int, int, int, int]]] = []

        actual_row: list[tuple[int, int, int, int]] = []
        for i, row in enumerate(icon3.rows):
            if row.data is None:
                continue

            if row.data.count_transparent > 0:
                actual_row.extend([(0, 0, 0, 0)] * row.data.count_transparent)

            for pixel in row.data.pixels:
                rgb = self.convert_555_to_888(pixel)
                actual_row.append((*rgb, 255))

            if (
                row.data.const_fe is not None
                or row.data.const_ff is not None
                and i < len(icon3.rows)
            ):
                actual_rows.append(actual_row)
                actual_row = []

        height = len(actual_rows)
        width = max(len(row) for row in actual_rows)

        img = Image.new("RGBA", (width, height), "black")

        for y, actual_row in enumerate(actual_rows):
            for x, (r, g, b, a) in enumerate(actual_row):
                img.putpixel((x, y), (r, g, b, a))

            if len(actual_row) < width:
                for x in range(len(actual_row), width):
                    img.putpixel((x, y), (0, 0, 0, 0))

        return img

    def convert_icon3_eight_bit(
        self, icon3_eight_bit: Icon3EightBit
    ) -> Image.Image | None:
        if len(icon3_eight_bit.rows) == 0 or not any(
            row.data is not None for row in icon3_eight_bit.rows
        ):
            return None

        actual_rows: list[list[tuple[int, int, int, int]]] = []

        actual_row: list[tuple[int, int, int, int]] = []
        for i, row in enumerate(icon3_eight_bit.rows):
            if row.data is None:
                continue

            if row.data.count_transparent > 0:
                actual_row.extend([(0, 0, 0, 0)] * row.data.count_transparent)

            for pixel in row.data.pixels:
                rgb = self.convert_332_to_888(pixel)
                actual_row.append((*rgb, 255))

            if (
                row.data.const_fe is not None
                or row.data.const_ff is not None
                and i < len(icon3_eight_bit.rows)
            ):
                actual_rows.append(actual_row)
                actual_row = []

        height = len(actual_rows)
        width = max(len(row) for row in actual_rows)

        img = Image.new("RGBA", (width, height), "black")

        for y, actual_row in enumerate(actual_rows):
            for x, (r, g, b, a) in enumerate(actual_row):
                img.putpixel((x, y), (r, g, b, a))

            if len(actual_row) < width:
                for x in range(len(actual_row), width):
                    img.putpixel((x, y), (0, 0, 0, 0))

        return img

    def convert_image_to_icon3(self, image: Image.Image) -> Icon3Write:
        rows: list[Icon3Row] = []
        icon3 = Icon3Write(rows)

        max_row_length = 255
        for y in range(image.height):
            row_pixels: list[int] = []
            count: int = 0
            for x in range(image.width):
                r, g, b, a = image.getpixel((x, y))
                # Convert 888 RGB to 555 RGB
                r_555 = (r * 31 // 255) & 0x1F
                g_555 = (g * 31 // 255) & 0x1F
                b_555 = (b * 31 // 255) & 0x1F
                color_555 = (r_555 << 10) | (g_555 << 5) | b_555
                row_pixels.append(color_555)
                count += 1

                row_data = Icon3RowData(
                    pixels=row_pixels,
                    const_fe=None,
                    const_ff=None,
                    count_transparent=0,
                    count=count,
                )
                row = Icon3Row(const_fe=None, const_ff=None, data=row_data)

                if len(row_pixels) == max_row_length:
                    icon3.rows.append(row)
                    row_pixels = []
                    count = 0

            row_data.count = count
            row_data.count_transparent = 0
            row_data.const_fe = 0xFE
            row_data.next_value = 0xFE
            icon3.rows.append(row)

        row_data.const_fe = None
        row_data.const_ff = 0xFF
        row_data.next_value = 0xFF

        return icon3
