from PIL import ImageDraw

from .font_manager import FontManager
from .image_handler import ImageHandler
from .text_box import TextBox


class ImageDrawer:
    def __init__(self, width, height, font_manager=None):
        self.image_handler = ImageHandler(width, height)
        self.font_manager = font_manager or FontManager()
        self.draw = ImageDraw.Draw(self.image_handler.image)

    def initialize(self):
        self.image_handler.initialize()
        self.draw = ImageDraw.Draw(self.image_handler.image)

    def change_size(self, width, height):
        """Changes the size of the image and re-initializes it."""
        self.image_handler.change_size(width, height)
        self.draw = ImageDraw.Draw(self.image_handler.image)

    def draw_text(
        self, text, start, end=None, font_name=None, font_variation=None, **kwargs
    ):
        """Draw text on the image with optional scaling to fit within a bounding box.

        - start: tuple (x1, y1) for the top-left corner.
        - end: optional tuple (x2, y2) for the bottom-right corner.
        If provided, the text will scale to fit within this box.
        """
        text_box = TextBox(text, self.font_manager)

        if end is not None:
            max_w, max_h = abs(end[0] - start[0]), abs(end[1] - start[1])
            font = text_box.fit_text(
                self.draw, max_w, max_h, font_name, font_variation=font_variation
            )
        else:
            font = self.font_manager.build_font(
                font_name, variation_name=font_variation
            )

        # Calculate the text size before drawing
        w, h = self.font_manager.calculate_text_size(self.draw, text, font)

        # Draw the text on the image
        text_box.draw_text(self.draw, start, font, **kwargs)

        # Return width, height, and font size for further usage
        return w, h, font.size

    def finalize(self, mirror=False, orientation=0, inverted=False):
        """Apply transformations and finalize the image."""
        self.image_handler.apply_transformations(
            mirror=mirror, orientation=orientation, inverted=inverted
        )

    def get_image(self):
        """Get the current image."""
        return self.image_handler.image

    def show(self, title=None):
        """Show the current image."""
        self.image_handler.show(title=title)

    def paste(self, im, box=None, mask=None):
        """Paste another image onto this one."""
        self.image_handler.image.paste(im, box=box, mask=mask)
