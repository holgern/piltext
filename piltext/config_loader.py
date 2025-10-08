"""YAML configuration loading for piltext image creation.

This module provides the ConfigLoader class for loading image, font, and grid
configurations from YAML files and creating corresponding piltext objects.
"""

import yaml
from PIL import ImageDraw

from .font_manager import FontManager
from .image_drawer import ImageDrawer
from .text_grid import TextGrid


class ConfigLoader:
    """Loads and processes YAML configuration files for image creation.

    ConfigLoader reads YAML configuration files and creates configured FontManager,
    ImageDrawer, and TextGrid objects. It supports font downloads, grid layouts,
    and image transformations defined in the configuration.

    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file.

    Attributes
    ----------
    config : dict
        Parsed YAML configuration dictionary.

    Examples
    --------
    >>> loader = ConfigLoader("config.yaml")
    >>> image = loader.render(output_path="output.png")

    Notes
    -----
    The YAML configuration file should contain sections for:
    - fonts: Font directories, default font, and downloads
    - image: Image dimensions, mode, background, and transformations
    - grid: Grid layout, margins, merges, and text content
    """

    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def create_font_manager(self):
        """Create a FontManager from the configuration.

        Reads the 'fonts' section of the configuration and creates a FontManager
        with the specified directories, default font, and font downloads.

        Returns
        -------
        FontManager
            Configured FontManager instance with downloaded fonts.

        Notes
        -----
        Font downloads support two formats:

        - Direct URL: {"url": "https://..."}
        - Google Fonts: {"part1": "ofl", "part2": "roboto",
          "font_name": "Roboto-Regular.ttf"}
        """
        font_config = self.config.get("fonts", {})
        fontdirs = font_config.get("directories")
        default_font_size = font_config.get("default_size", 15)
        default_font_name = font_config.get("default_name")

        fm = FontManager(
            fontdirs=fontdirs,
            default_font_size=default_font_size,
            default_font_name=default_font_name,
        )

        downloads = font_config.get("download", [])
        for download in downloads:
            if "url" in download:
                fm.download_font(download["url"])
            elif all(k in download for k in ["part1", "part2", "font_name"]):
                fm.download_google_font(
                    download["part1"], download["part2"], download["font_name"]
                )

        return fm

    def create_image_drawer(self, font_manager=None):
        """Create an ImageDrawer from the configuration.

        Reads the 'image' section of the configuration and creates an ImageDrawer
        with the specified dimensions, mode, and background color.

        Parameters
        ----------
        font_manager : FontManager, optional
            FontManager to use. If None, creates a new one from the configuration.

        Returns
        -------
        ImageDrawer
            Configured ImageDrawer instance ready for drawing.
        """
        image_config = self.config.get("image", {})
        width = image_config.get("width", 480)
        height = image_config.get("height", 280)
        mode = image_config.get("mode", "RGB")
        background = image_config.get("background", "white")

        if font_manager is None:
            font_manager = self.create_font_manager()

        image_drawer = ImageDrawer(width, height, font_manager)
        image_drawer.image_handler.mode = mode
        image_drawer.image_handler.background = background
        image_drawer.image_handler.initialize()
        image_drawer.draw = ImageDraw.Draw(image_drawer.image_handler.image)

        return image_drawer

    def create_grid(self, image_drawer=None, font_manager=None):
        """Create a TextGrid from the configuration.

        Reads the 'grid' section of the configuration and creates a TextGrid
        with the specified layout, margins, and cell merges.

        Parameters
        ----------
        image_drawer : ImageDrawer, optional
            ImageDrawer to use for the grid. If None, creates a new one.
        font_manager : FontManager, optional
            FontManager to use. If None and image_drawer is None, creates a new one.

        Returns
        -------
        TextGrid or None
            Configured TextGrid instance, or None if no grid configuration exists.

        Notes
        -----
        Cell merges should be specified as a list of
        [[start_row, start_col], [end_row, end_col]] pairs.
        """
        grid_config = self.config.get("grid")
        if not grid_config:
            return None

        if image_drawer is None:
            image_drawer = self.create_image_drawer(font_manager)

        rows = grid_config.get("rows", 1)
        columns = grid_config.get("columns", 1)
        margin_x = grid_config.get("margin_x", 0)
        margin_y = grid_config.get("margin_y", 0)

        grid = TextGrid(rows, columns, image_drawer, margin_x, margin_y)

        merge_list = grid_config.get("merge", [])
        if merge_list:
            formatted_merge = []
            for merge_item in merge_list:
                if isinstance(merge_item, list) and len(merge_item) == 2:
                    start = tuple(merge_item[0])
                    end = tuple(merge_item[1])
                    formatted_merge.append((start, end))
            if formatted_merge:
                grid.merge_bulk(formatted_merge)

        return grid

    def render(self, output_path=None):
        """Render the complete image from the configuration.

        Creates all configured objects (FontManager, ImageDrawer, TextGrid),
        renders the text content, applies transformations, and optionally saves
        the result to a file.

        Parameters
        ----------
        output_path : str, optional
            Path to save the rendered image. If None, the image is not saved
            to disk.

        Returns
        -------
        PIL.Image.Image
            The rendered image with all text and transformations applied.

        Notes
        -----
        The rendering process follows these steps:
        1. Create FontManager and download fonts
        2. Create ImageDrawer with configured dimensions
        3. Create TextGrid if configured
        4. Render all text from the grid configuration
        5. Apply transformations (mirror, rotation, inversion)
        6. Save to file if output_path is provided
        """
        font_manager = self.create_font_manager()
        image_drawer = self.create_image_drawer(font_manager)

        grid = self.create_grid(image_drawer, font_manager)

        if grid:
            grid_config = self.config.get("grid", {})
            text_list = grid_config.get("texts", [])
            if text_list:
                for text_item in text_list:
                    if "start" in text_item and isinstance(text_item["start"], list):
                        text_item["start"] = tuple(text_item["start"])
                    if "end" in text_item and isinstance(text_item["end"], list):
                        text_item["end"] = tuple(text_item["end"])
                grid.set_text_list(text_list)

        image_config = self.config.get("image", {})
        mirror = image_config.get("mirror", False)
        orientation = image_config.get("orientation", 0)
        inverted = image_config.get("inverted", False)

        image_drawer.finalize(mirror=mirror, orientation=orientation, inverted=inverted)

        if output_path:
            image_drawer.image_handler.image.save(output_path)

        return image_drawer.get_image()
