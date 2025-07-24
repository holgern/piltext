from typing import Any

from PIL import Image, ImageOps


class ImageHandler:
    def __init__(
        self, width: int, height: int, mode: str = "L", background: Any = 255
    ) -> None:
        self.width = width
        self.height = height
        self.mode = mode
        self.background = background
        self.initialize()

    def initialize(self) -> None:
        """Initialize the image with the given width, height, and mode."""
        self.image = Image.new(self.mode, (self.width, self.height), self.background)

    def change_size(self, width: int, height: int) -> None:
        """Changes the size of the image and re-initializes it."""
        self.width = width
        self.height = height
        self.initialize()  # Reinitialize the image with the new size

    def apply_transformations(
        self, mirror: bool = False, orientation: int = 0, inverted: bool = False
    ) -> None:
        """Apply transformations like mirroring, rotating, or inverting."""
        if orientation:
            self.image = self.image.rotate(orientation, expand=True)
        if mirror:
            self.image = ImageOps.mirror(self.image)
        if inverted:
            self.image = ImageOps.invert(self.image)

    def show(self, title: str | None = None) -> None:
        """Display the image."""
        # PIL.Image.show() does not accept 'title' in all versions
        if title is not None:
            try:
                self.image.show(title=title)
            except TypeError:
                self.image.show()
        else:
            self.image.show()

    def paste(self, im: Any, box: tuple | None = None, mask: Any | None = None) -> None:
        """Paste another image onto this one."""
        self.image.paste(im, box=box, mask=mask)
