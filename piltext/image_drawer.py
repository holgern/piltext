"""Core image drawing functionality for text rendering.

This module provides the ImageDrawer class, which combines image handling,
font management, and text rendering into a unified interface.
"""

from PIL import ImageDraw

from .font_manager import FontManager
from .image_handler import ImageHandler
from .text_box import TextBox


class ImageDrawer:
    """High-level interface for drawing text on images.

    ImageDrawer combines ImageHandler, FontManager, and TextBox functionality
    to provide a simple API for creating images with text. It handles image
    initialization, text scaling, and image transformations.

    Parameters
    ----------
    width : int
        Width of the image in pixels.
    height : int
        Height of the image in pixels.
    font_manager : FontManager, optional
        FontManager instance to use for font operations. If None, a default
        FontManager is created.

    Attributes
    ----------
    image_handler : ImageHandler
        Handles image creation and transformations.
    font_manager : FontManager
        Manages font loading and caching.
    draw : PIL.ImageDraw.ImageDraw
        PIL drawing context for the image.

    Examples
    --------
    >>> drawer = ImageDrawer(800, 600)
    >>> drawer.draw_text("Hello World", (100, 100), font_size=24)
    >>> drawer.finalize()
    >>> drawer.show()
    """

    def __init__(self, width, height, font_manager=None):
        self.image_handler = ImageHandler(width, height)
        self.font_manager = font_manager or FontManager()
        self.draw = ImageDraw.Draw(self.image_handler.image)

    def initialize(self):
        """Reinitialize the image to a blank state.

        Clears the current image and creates a fresh drawing context. Useful for
        reusing the same ImageDrawer instance for multiple images.
        """
        self.image_handler.initialize()
        self.draw = ImageDraw.Draw(self.image_handler.image)

    def change_size(self, width, height):
        """Change the dimensions of the image and reinitialize.

        Resizes the image to new dimensions and creates a fresh drawing context.
        All existing content on the image is lost.

        Parameters
        ----------
        width : int
            New width in pixels.
        height : int
            New height in pixels.
        """
        self.image_handler.change_size(width, height)
        self.draw = ImageDraw.Draw(self.image_handler.image)

    def draw_text(
        self,
        text,
        start,
        end=None,
        font_name=None,
        font_size=None,
        font_variation=None,
        measure_only=False,
        **kwargs,
    ):
        """Draw text on the image with optional automatic scaling.

        Renders text at the specified position. If an end position is provided,
        the text is automatically scaled to fit within the bounding box. Supports
        additional PIL text drawing options via kwargs.

        Parameters
        ----------
        text : str
            Text string to render.
        start : tuple of (int, int)
            Top-left corner position (x1, y1) for the text.
        end : tuple of (int, int), optional
            Bottom-right corner position (x2, y2). If provided, text is scaled
            to fit within the bounding box defined by start and end.
        font_name : str, optional
            Name of the font to use. If None, uses the default font.
        font_size : int, optional
            Font size in points. Ignored if end is provided (auto-scaling).
        font_variation : str, optional
            Named variation for variable fonts (e.g., 'Bold', 'Italic').
        measure_only : bool, default=False
            If True, only calculates text size without drawing.
        **kwargs : dict
            Additional keyword arguments passed to PIL's text drawing method
            (e.g., fill, stroke_width, stroke_fill).

        Returns
        -------
        tuple of (int, int, int)
            Width, height, and font size of the rendered text.
        """
        text_box = TextBox(text, self.font_manager)

        if end is not None:
            max_w, max_h = abs(end[0] - start[0]), abs(end[1] - start[1])
            font = text_box.fit_text(
                self.draw, max_w, max_h, font_name, font_variation=font_variation
            )
        else:
            font = self.font_manager.build_font(
                font_name, font_size=font_size, variation_name=font_variation
            )

        # Calculate the text size before drawing
        w, h = self.font_manager.calculate_text_size(self.draw, text, font)
        if not measure_only:
            # Draw the text on the image
            text_box.draw_text(self.draw, start, font, **kwargs)

        # Return width, height, and font size for further usage
        return w, h, font.size

    def finalize(self, mirror=False, orientation=0, inverted=False):
        """Apply final transformations to the image.

        Applies mirror, rotation, and color inversion transformations to the
        image before saving or displaying.

        Parameters
        ----------
        mirror : bool, default=False
            If True, mirrors the image horizontally.
        orientation : int, default=0
            Rotation angle in degrees (0, 90, 180, or 270).
        inverted : bool, default=False
            If True, inverts the image colors.
        """
        self.image_handler.apply_transformations(
            mirror=mirror, orientation=orientation, inverted=inverted
        )

    def get_image(self):
        """Get the current PIL Image object.

        Returns
        -------
        PIL.Image.Image
            The current image with all applied drawing operations.
        """
        return self.image_handler.image

    def show(self, title=None):
        """Display the image in the default image viewer.

        Opens the image in the system's default image viewing application.

        Parameters
        ----------
        title : str, optional
            Window title for the image viewer.
        """
        self.image_handler.show(title=title)

    def paste(self, im, box=None, mask=None):
        """Paste another image onto the current image.

        Composites another image onto this image at the specified position.

        Parameters
        ----------
        im : PIL.Image.Image
            Image to paste.
        box : tuple of (int, int) or tuple of (int, int, int, int), optional
            Position to paste the image. Can be (x, y) for top-left corner or
            (x1, y1, x2, y2) for a bounding box.
        mask : PIL.Image.Image, optional
            Mask image for transparency. Must be mode '1', 'L', or 'RGBA'.
        """
        self.image_handler.image.paste(im, box=box, mask=mask)
