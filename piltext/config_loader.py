import yaml

from .font_manager import FontManager
from .image_drawer import ImageDrawer
from .text_grid import TextGrid


class ConfigLoader:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def create_font_manager(self):
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
        image_config = self.config.get("image", {})
        width = image_config.get("width", 480)
        height = image_config.get("height", 280)

        if font_manager is None:
            font_manager = self.create_font_manager()

        return ImageDrawer(width, height, font_manager)

    def create_grid(self, image_drawer=None, font_manager=None):
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
