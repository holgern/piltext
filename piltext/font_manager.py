import logging
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote
from urllib.request import urlopen

from PIL import ImageDraw, ImageFont

_logger = logging.getLogger(__name__)


class FontManager:
    def __init__(self, fontdirs=None, default_font_size=15, default_font_name=None):
        # Use the default font directory if none provided
        if fontdirs is None:
            default_fontdir = self.get_user_font_dir()
            fontdirs = [default_fontdir]
        elif isinstance(
            fontdirs, str
        ):  # Allow single directory as a string for backward compatibility
            fontdirs = [fontdirs]

        self.fontdirs = [os.path.realpath(fontdir) for fontdir in fontdirs]
        self.default_font_name = default_font_name
        self.default_font_size = default_font_size
        self._font_cache = {}

    def get_user_font_dir(self):
        """Returns the user font directory based on the OS."""
        if os.name == "nt":  # Windows
            font_dir = os.path.join(os.getenv("APPDATA"), "piltext")
        elif os.name == "posix":  # macOS and Linux
            font_dir = os.path.join(os.path.expanduser("~"), ".config", "piltext")
        else:
            raise OSError("Unsupported operating system")
        # Create the directory if it doesn't exist
        if not os.path.exists(font_dir):
            os.makedirs(font_dir)
        return str(font_dir)

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

    def download_google_font(self, part1, part2, font_name):
        google_font_url = (
            "https://github.com/google/fonts/blob/"
            f"main/{part1}/{quote(part2)}/{quote(font_name)}?raw=true"
        )
        return self.download_font(google_font_url)

    def download_font(self, font_url):
        """Downloads a list of fonts and stores them in the user font directory."""
        font_dir = self.fontdirs[0]

        font_name = unquote(
            font_url.split("/")[-1].split("?")[0]
        )  # Extract font filename
        font_path = os.path.join(font_dir, font_name)

        if not os.path.exists(font_path):
            try:
                response = urlopen(font_url)
                with open(font_path, "wb") as font_file:
                    font_file.write(response.read())
            except HTTPError as e:
                if e.code == 404:
                    raise Exception(
                        "404 error. The url passed does not exist: font file not found."
                    ) from e

            except URLError as e:
                raise Exception(
                    "Failed to load font. This may be due "
                    "to a lack of internet connection."
                ) from e
        return os.path.splitext(font_path)[0]

    def calculate_text_size(self, draw: ImageDraw, text, font):
        """Calculate the size of the text."""
        _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
        return width, height

    def get_variation_names(self, font_name=None):
        font = self.build_font(font_name=font_name)
        return font.get_variation_names()

    def build_font(self, font_name=None, font_size=None, variation_name=None):
        """Create and cache font objects."""
        font_size = font_size or self.default_font_size
        font_name = font_name or self.default_font_name
        variation_name = variation_name or "none"
        cache_key = (font_name, font_size, variation_name)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        font_path = self.get_full_path(font_name)
        font = ImageFont.truetype(font_path, font_size)
        if variation_name != "none":
            font.set_variation_by_name(variation_name)
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

    def list_available_fonts(self, fullpath=False):
        """List all available font files in the font directories without file
        extensions."""
        available_fonts = set()
        for fontdir in self.fontdirs:
            if os.path.exists(fontdir) and os.path.isdir(fontdir):
                for file in os.listdir(fontdir):
                    if file.endswith((".ttf", ".otf")):
                        # Add the font name without extension to the set
                        if fullpath:
                            available_fonts.add(os.path.join(fontdir, file))
                        else:
                            available_fonts.add(os.path.splitext(file)[0])
        return list(available_fonts)

    def delete_all_fonts(self):
        """Deletes all font files in
        the user font directory."""
        deleted_fonts = []
        for font_dir in self.fontdirs:
            for font_file_name in os.listdir(font_dir):
                if not font_file_name.endswith((".ttf", ".otf")):
                    continue
                font_file_path = os.path.join(font_dir, font_file_name)
                if os.path.isfile(font_file_path):
                    os.remove(font_file_path)
                    deleted_fonts.append(font_file_name)
        return deleted_fonts
