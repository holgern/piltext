import logging
import os

from PIL import ImageDraw, ImageFont

_logger = logging.getLogger(__name__)


class FontManager:
    def __init__(self, fontdirs=None, default_font_size=15, default_font_name=None):
        # Use the default font directory if none provided
        if fontdirs is None:
            default_fontdir = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "fonts"
            )
            fontdirs = [default_fontdir]
        elif isinstance(
            fontdirs, str
        ):  # Allow single directory as a string for backward compatibility
            fontdirs = [fontdirs]

        self.fontdirs = [os.path.realpath(fontdir) for fontdir in fontdirs]
        self.default_font_name = default_font_name
        self.default_font_size = default_font_size
        self._font_cache = {}

    def get_full_path(self, font_name):
        """Get the full path of the font file, checking all directories."""
        for fontdir in self.fontdirs:
            font_path = os.path.join(fontdir, font_name)
            for ext in ["", ".ttf", ".otf"]:
                if os.path.exists(font_path + ext):
                    return font_path + ext
        raise FileNotFoundError(
            f"Font '{font_name}' not found in directories: {self.fontdirs}"
        )

    def calculate_text_size(self, draw: ImageDraw, text, font):
        """Calculate the size of the text."""
        _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
        return width, height

    def build_font(self, font_name=None, font_size=None):
        """Create and cache font objects."""
        font_size = font_size or self.default_font_size
        font_name = font_name or self.default_font_name
        cache_key = (font_name, font_size)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        font_path = self.get_full_path(font_name)
        font = ImageFont.truetype(font_path, font_size)
        self._font_cache[cache_key] = font
        return font

    def add_font_directory(self, fontdir):
        """Add a new font directory to the list."""
        if fontdir not in self.fontdirs:
            self.fontdirs.append(os.path.realpath(fontdir))
        else:
            print(f"Font directory '{fontdir}' already exists.")

    def remove_font_directory(self, fontdir):
        """Remove a font directory from the list."""
        if fontdir in self.fontdirs:
            self.fontdirs.remove(os.path.realpath(fontdir))
        else:
            print(f"Font directory '{fontdir}' not found in the list.")

    def list_font_directories(self):
        """List all available font directories."""
        return self.fontdirs

    def list_available_fonts(self):
        """List all available font files in the font directories without file
        extensions."""
        available_fonts = set()
        for fontdir in self.fontdirs:
            if os.path.exists(fontdir) and os.path.isdir(fontdir):
                for file in os.listdir(fontdir):
                    if file.endswith((".ttf", ".otf")):
                        # Add the font name without extension to the set
                        available_fonts.add(os.path.splitext(file)[0])
        return list(available_fonts)
