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
    anchors: Optional[list[Optional[str]]] = None,
    grid_info: Optional[dict] = None,
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
    anchors : list[str or None], optional
        List of anchor positions for each text item (e.g., 'mm', 'lt', 'rb').
        Default is None.
    grid_info : dict, optional
        Grid layout information including rows, columns, and merge cells.
        Default is None.

    Returns
    -------
    str
        Formatted text output with optional ANSI color codes.
    """
    if grid_info is not None:
        return _display_grid_text(texts, width, colors, anchors, grid_info)

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


def _get_cell_position(
    i: int,
    merge_cells: list,
    text_items: list[dict],
) -> Optional[tuple[tuple[int, int], tuple[int, int]]]:
    """
    Get start and end positions for a text item in the grid.
    """
    if merge_cells and i < len(merge_cells):
        return merge_cells[i][0], merge_cells[i][1]
    elif i < len(text_items) and "start" in text_items[i]:
        start_pos = text_items[i]["start"]
        end_pos = text_items[i].get("end", start_pos)
        return start_pos, end_pos
    return None


def _align_text(text: str, cell_w: int, h_align: str) -> str:
    """
    Align text horizontally within a cell.
    """
    text_truncated = text[:cell_w] if len(text) > cell_w else text
    if h_align == "l":
        return text_truncated.ljust(cell_w)
    elif h_align == "r":
        return text_truncated.rjust(cell_w)
    else:
        return text_truncated.center(cell_w)


def _apply_color(
    text: str,
    color: Optional[Union[str, int]],
) -> str:
    """
    Apply ANSI color code to text if color is provided.
    """
    if color is not None and isinstance(color, str) and color.startswith("#"):
        ansi_code = _hex_to_ansi(color)
        return f"{ansi_code}{text}\033[0m"
    return text


def _get_text_row(
    v_align: str,
    start_row: int,
    end_row: int,
    cell_height: int,
    cell_h: int,
) -> int:
    """
    Calculate the row position for text based on vertical alignment.
    """
    if v_align == "t":
        return start_row * cell_height
    elif v_align == "b":
        return (end_row + 1) * cell_height - 1
    else:
        return start_row * cell_height + cell_h // 2


def _build_grid_line(
    aligned_text: str,
    grid_row: list[str],
    start_col: int,
    end_col: int,
    columns: int,
    cell_width: int,
) -> list[str]:
    """
    Build a single line of the grid with the aligned text.
    """
    line_parts = []
    char_idx = 0
    for col in range(columns):
        if col >= start_col and col <= end_col:
            chars_in_cell = min(cell_width, len(aligned_text) - char_idx)
            if chars_in_cell > 0:
                line_parts.append(aligned_text[char_idx : char_idx + chars_in_cell])
                char_idx += chars_in_cell
            else:
                line_parts.append(" " * cell_width)
        else:
            line_parts.append(grid_row[col])
    return line_parts


def _display_grid_text(
    texts: list[str],
    width: int,
    colors: Optional[list[Optional[Union[str, int]]]],
    anchors: Optional[list[Optional[str]]],
    grid_info: dict,
) -> str:
    """
    Display text in a grid layout preserving position information.
    """
    rows = grid_info.get("rows", 1)
    columns = grid_info.get("columns", 1)
    merge_cells = grid_info.get("merge", [])
    text_items = grid_info.get("texts", [])

    colors_list = colors if colors else [None] * len(texts)
    anchors_list = anchors if anchors else [None] * len(texts)

    max_row = (
        max([merge[1][0] for merge in merge_cells] + [rows - 1])
        if merge_cells
        else rows - 1
    )
    actual_rows = max_row + 1
    cell_width = width // columns
    cell_height = 3

    grid = [
        [" " * cell_width for _ in range(columns)]
        for _ in range(actual_rows * cell_height)
    ]

    for i, text in enumerate(texts):
        position = _get_cell_position(i, merge_cells, text_items)
        if position is None:
            continue

        start_pos, end_pos = position
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        cell_w = (end_col - start_col + 1) * cell_width
        cell_h = (end_row - start_row + 1) * cell_height

        anchor = anchors_list[i] if i < len(anchors_list) else "mm"
        anchor = anchor or "mm"

        v_align = anchor[0] if len(anchor) > 0 else "m"
        h_align = anchor[1] if len(anchor) > 1 else "m"

        aligned_text = _align_text(text, cell_w, h_align)
        color = colors_list[i] if i < len(colors_list) else None
        aligned_text = _apply_color(aligned_text, color)

        text_row = _get_text_row(v_align, start_row, end_row, cell_height, cell_h)

        if text_row < len(grid):
            grid[text_row] = _build_grid_line(
                aligned_text,
                grid[text_row],
                start_col,
                end_col,
                columns,
                cell_width,
            )

    output_lines = [("".join(row)).rstrip() for row in grid]
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
