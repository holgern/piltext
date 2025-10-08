"""
ASCII art image conversion.

This module provides utilities for converting PIL images to ASCII art
representations. It supports both colored (using ANSI escape codes) and
monochrome ASCII output.

Examples
--------
Convert an image to colored ASCII art:

>>> from PIL import Image
>>> from piltext.ascii_art import display_as_ascii
>>> img = Image.open("example.png")
>>> ascii_art = display_as_ascii(img, columns=80)
>>> print(ascii_art)

Convert to monochrome ASCII art:

>>> ascii_art = display_as_ascii(img, columns=60, monochrome=True)
>>> print(ascii_art)

Use custom characters:

>>> ascii_art = display_as_ascii(img, char="█▓▒░ ", columns=100)
>>> print(ascii_art)
"""

from typing import Optional, Union

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


def _hex_to_ansi(hex_color: str) -> str:
    """
    Convert hex color (#RRGGBB) to closest ANSI color code.

    Parameters
    ----------
    hex_color : str
        Hex color string in format #RRGGBB.

    Returns
    -------
    str
        ANSI escape code for the closest matching color.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    min_distance = float("inf")
    best_code = "\033[37m"

    for palette_rgb, ansi_code, _ in PALETTE:
        palette_r = int(palette_rgb[0] * 255)
        palette_g = int(palette_rgb[1] * 255)
        palette_b = int(palette_rgb[2] * 255)

        distance = (r - palette_r) ** 2 + (g - palette_g) ** 2 + (b - palette_b) ** 2

        if distance < min_distance:
            min_distance = distance
            best_code = ansi_code

    return best_code


def display_readable_text(
    texts: list[str],
    width: int = 80,
    line_spacing: int = 1,
    center: bool = True,
    colors: Optional[list[Optional[Union[str, int]]]] = None,
) -> str:
    """
    Display text content in readable ASCII format.

    Parameters
    ----------
    texts : list[str]
        List of text strings to display.
    width : int, optional
        Width for centering text. Default is 80.
    line_spacing : int, optional
        Number of blank lines between text items. Default is 1.
    center : bool, optional
        Whether to center text. Default is True.
    colors : list[str or int or None], optional
        List of colors for each text item. Can be hex strings (#RRGGBB),
        integers (grayscale), or None. Default is None.

    Returns
    -------
    str
        Formatted text output with optional ANSI color codes.
    """
    if colors is None:
        colors_list: list[Optional[Union[str, int]]] = [None] * len(texts)
    else:
        colors_list = colors

    output_lines = []

    for i, text in enumerate(texts):
        color = colors_list[i] if i < len(colors_list) else None

        if center:
            centered_text = text.center(width)
        else:
            centered_text = text

        if color is not None:
            if isinstance(color, str) and color.startswith("#"):
                ansi_code = _hex_to_ansi(color)
                output_lines.append(f"{ansi_code}{centered_text}\033[0m")
            elif isinstance(color, int):
                output_lines.append(centered_text)
            else:
                output_lines.append(centered_text)
        else:
            output_lines.append(centered_text)

        if i < len(texts) - 1:
            output_lines.extend([""] * line_spacing)

    return "\n".join(output_lines)


def generate_ascii_art_text(
    texts: list[str],
    font: str = "standard",
    width: Optional[int] = None,
    line_spacing: int = 1,
    colors: Optional[list[Optional[Union[str, int]]]] = None,
) -> str:
    """
    Generate large FIGlet-style ASCII art text.

    Parameters
    ----------
    texts : list[str]
        List of text strings to convert to ASCII art.
    font : str, optional
        FIGlet font name (e.g., 'standard', 'slant', 'banner'). Default is 'standard'.
    width : int, optional
        Maximum width for the output. Default is None (no limit).
    line_spacing : int, optional
        Number of blank lines between text items. Default is 1.
    colors : list[str or int or None], optional
        List of colors for each text item. Can be hex strings (#RRGGBB),
        integers (grayscale), or None. Default is None.

    Returns
    -------
    str
        ASCII art representation of the text with optional ANSI color codes.

    Raises
    ------
    ImportError
        If pyfiglet is not installed.
    """
    try:
        from pyfiglet import Figlet  # type: ignore
    except ImportError as e:
        raise ImportError(
            "pyfiglet is required for FIGlet output. Install with: pip install pyfiglet"
        ) from e

    if colors is None:
        colors_list: list[Optional[Union[str, int]]] = [None] * len(texts)
    else:
        colors_list = colors

    figlet = Figlet(font=font, width=width or 10000)

    output_lines = []

    for i, text in enumerate(texts):
        ascii_art = figlet.renderText(text)
        color = colors_list[i] if i < len(colors_list) else None

        if color is not None and isinstance(color, str) and color.startswith("#"):
            ansi_code = _hex_to_ansi(color)
            colored_lines = [
                f"{ansi_code}{line}\033[0m" for line in ascii_art.split("\n")
            ]
            output_lines.extend(colored_lines)
        else:
            output_lines.extend(ascii_art.split("\n"))

        if i < len(texts) - 1:
            output_lines.extend([""] * line_spacing)

    return "\n".join(output_lines)


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
    img: Image.Image,
    columns: int = 80,
    width_ratio: float = 2.2,
    char: Optional[str] = None,
    monochrome: bool = False,
) -> str:
    """
    Convert a PIL Image to ASCII art representation.

    Parameters
    ----------
    img : PIL.Image.Image
        The image to convert to ASCII art.
    columns : int, optional
        Target width in characters for the ASCII output. Default is 80.
    width_ratio : float, optional
        Character aspect ratio adjustment (characters are typically taller
        than they are wide). Default is 2.2.
    char : str, optional
        Custom characters to use for rendering, ordered from darkest to
        brightest. If None, uses default characters " .:−=+*#%@".
    monochrome : bool, optional
        If True, output monochrome ASCII without ANSI color codes.
        If False, use ANSI escape codes for colored output. Default is False.

    Returns
    -------
    str
        The ASCII art representation of the image, with newlines separating
        rows. If colored, includes ANSI escape codes.

    Examples
    --------
    Basic colored ASCII art:

    >>> from PIL import Image
    >>> img = Image.open("photo.jpg")
    >>> ascii_art = display_as_ascii(img, columns=80)
    >>> print(ascii_art)

    Monochrome ASCII art with custom width:

    >>> ascii_art = display_as_ascii(img, columns=60, monochrome=True)
    >>> print(ascii_art)

    Custom character set:

    >>> ascii_art = display_as_ascii(img, char="█▓▒░ ", columns=100)
    >>> print(ascii_art)

    Notes
    -----
    - The image is automatically resized to fit the specified column width
    - Brightness is calculated from the grayscale version of the image
    - Color matching (when not monochrome) uses a predefined 16-color palette
    - The aspect ratio is adjusted using width_ratio to account for terminal
      character dimensions
    """
    img_w, img_h = img.size
    scalar = img_w * width_ratio / columns
    img_w = int(img_w * width_ratio / scalar)
    img_h = int(img_h / scalar)

    rgb_img = img.resize((img_w, img_h))
    color_palette = img.getpalette()

    grayscale_img = rgb_img.convert("L")

    chars = list(char) if char else [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]

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
