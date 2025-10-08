from typing import Optional

from PIL import Image

PALETTE = [
    [(0.0, 0.0, 0.0), "\033[30m", "#000000"],
    [(0.5, 0.0, 0.0), "\033[31m", "#800000"],
    [(0.0, 0.5, 0.0), "\033[32m", "#008000"],
    [(0.5, 0.5, 0.0), "\033[33m", "#808000"],
    [(0.0, 0.0, 0.5), "\033[34m", "#000080"],
    [(0.5, 0.0, 0.5), "\033[35m", "#800080"],
    [(0.0, 0.5, 0.5), "\033[36m", "#008080"],
    [(0.75, 0.75, 0.75), "\033[37m", "#c0c0c0"],
    [(0.5, 0.5, 0.5), "\033[90m", "#808080"],
    [(1.0, 0.0, 0.0), "\033[91m", "#ff0000"],
    [(0.0, 1.0, 0.0), "\033[92m", "#00ff00"],
    [(1.0, 1.0, 0.0), "\033[93m", "#ffff00"],
    [(0.0, 0.0, 1.0), "\033[94m", "#0000ff"],
    [(1.0, 0.0, 1.0), "\033[95m", "#ff00ff"],
    [(0.0, 1.0, 1.0), "\033[96m", "#00ffff"],
    [(1.0, 1.0, 1.0), "\033[97m", "#ffffff"],
]


def _l2_min(v1: list, v2: list) -> float:
    return (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2 + (v1[2] - v2[2]) ** 2


def _convert_color(rgb: list, brightness: float) -> str:
    min_distance = 2.0
    index = 0

    for i in range(len(PALETTE)):
        tmp = [v * brightness for v in PALETTE[i][0]]
        distance = _l2_min(tmp, rgb)

        if distance < min_distance:
            index = i
            min_distance = distance

    return PALETTE[index][1]


def display_as_ascii(
    image_path: str,
    columns: int = 80,
    width_ratio: float = 2.2,
    char: Optional[str] = None,
    monochrome: bool = False,
) -> str:
    img = Image.open(image_path)

    img_w, img_h = img.size
    scalar = img_w * width_ratio / columns
    img_w = int(img_w * width_ratio / scalar)
    img_h = int(img_h / scalar)

    rgb_img = img.resize((img_w, img_h))
    color_palette = img.getpalette()

    grayscale_img = rgb_img.convert("L")

    chars = [char] if char else [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]

    lines = []
    previous_color = ""
    for h in range(img_h):
        line = ""

        for w in range(img_w):
            brightness_pixel = grayscale_img.getpixel((w, h))
            if isinstance(brightness_pixel, (int, float)):
                brightness = brightness_pixel / 255
            else:
                brightness = 0.0

            pixel = rgb_img.getpixel((w, h))

            if isinstance(pixel, int):
                pixel = (
                    (pixel, pixel, 255)
                    if color_palette is None
                    else tuple(color_palette[pixel * 3 : pixel * 3 + 3])
                )

            ascii_char = chars[int(brightness * (len(chars) - 1))]

            if monochrome:
                line += ascii_char
            else:
                if isinstance(pixel, tuple) and len(pixel) >= 3:
                    srgb = [(v / 255.0) ** 2.2 for v in pixel[:3]]
                    color_code = _convert_color(srgb, brightness)
                    if color_code == previous_color:
                        line += ascii_char
                    else:
                        line += color_code + ascii_char
                        previous_color = color_code
                else:
                    line += ascii_char

        lines.append(line)

    if monochrome:
        return "\n".join(lines)
    else:
        return "\n".join(lines) + "\033[0m"
