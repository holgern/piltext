from PIL import Image, ImageOps


class ImageHandler:
    def __init__(self, width, height, mode="L", background=255):
        self.width = width
        self.height = height
        self.mode = mode
        self.background = background
        self.image = False
        self.initialize()

    def initialize(self):
        """Initialize the image with the given width, height, and mode."""
        self.image = Image.new(self.mode, (self.width, self.height), self.background)

    def change_size(self, width, height):
        """Changes the size of the image and re-initializes it."""
        self.width = width
        self.height = height
        self.initialize()  # Reinitialize the image with the new size

    def apply_transformations(self, mirror=False, orientation=0, inverted=False):
        """Apply transformations like mirroring, rotating, or inverting."""
        if orientation:
            self.image = self.image.rotate(orientation, expand=True)
        if mirror:
            self.image = ImageOps.mirror(self.image)
        if inverted:
            self.image = ImageOps.invert(self.image)

    def show(self, title=None):
        """Display the image."""
        self.image.show(title=title)

    def paste(self, im, box=None, mask=None):
        """Paste another image onto this one."""
        self.image.paste(im, box=box, mask=mask)
