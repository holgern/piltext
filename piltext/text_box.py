from PIL import ImageDraw

from .font_manager import FontManager


class TextBox:
    def __init__(self, text, font_manager: FontManager):
        self.text = text
        self.font_manager = font_manager

    def fit_text(
        self,
        draw: ImageDraw,
        max_width: int,
        max_height: int,
        font_name=None,
        font_variation=None,
        start_font_size: int = 1,
    ):
        """Determine the largest font size that fits within max_width and max_height."""
        font_size = start_font_size
        font = self.font_manager.build_font(
            font_name, font_size, variation_name=font_variation
        )
        while True:
            width, height = self.font_manager.calculate_text_size(draw, self.text, font)
            if width > max_width or height > max_height:
                font_size -= 1
                if font_size < 1:
                    font_size = 1
                return self.font_manager.build_font(
                    font_name, font_size, variation_name=font_variation
                )
            font_size += 1
            font = self.font_manager.build_font(
                font_name, font_size, variation_name=font_variation
            )
        return font

    def draw_text(self, draw: ImageDraw, xy, font, **kwargs):
        """Draw the text using the given font."""
        draw.text(xy, self.text, font=font, **kwargs)
