import unittest
from unittest.mock import MagicMock

from PIL import Image

from piltext import TextGrid


# Mock classes for FontManager and ImageDrawer, assuming they are correctly implemented
class MockFontManager:
    def __init__(self, *args, **kwargs):
        pass

    def build_font(self, font_name=None):
        return MagicMock()

    def calculate_text_size(self, draw, text, font):
        # Mocked to return a fixed width and height for testing purposes
        return (100, 50)


class MockImageHandler:
    def __init__(self, width, height):
        self.image = Image.new("RGB", (width, height), color="white")

    def apply_transformations(self, *args, **kwargs):
        pass

    def show(self, *args, **kwargs):
        pass


class MockImageDrawer:
    def __init__(self, width, height, font_manager=None):
        self.image_handler = MockImageHandler(width, height)
        self.font_manager = font_manager or MockFontManager()
        self.draw = MagicMock()  # Mock drawing operations

    def draw_text(self, text, start, end=None, font_name=None, **kwargs):
        # Mock the draw_text method to check that
        # it's being called with correct parameters
        self.draw.text((start, text, font_name))

    def finalize(self, inverted=False):
        pass

    def get_image(self):
        return self.image_handler.image


class TestGrid(unittest.TestCase):
    def setUp(self):
        font_manager = MockFontManager()
        self.image_drawer = MockImageDrawer(480, 280, font_manager)
        self.image_drawer.draw_text = MagicMock()

        self.grid = TextGrid(4, 4, self.image_drawer)  # 4x4 grid

    def test_grid_cell_size(self):
        """Test that the grid cells are the correct size."""
        self.assertEqual(self.grid.cell_width, 120)  # 480 / 4
        self.assertEqual(self.grid.cell_height, 70)  # 280 / 4

    def test_grid_to_pixels(self):
        """Test that grid coordinates are correctly converted to pixel coordinates."""
        start_pixel, end_pixel = self.grid._grid_to_pixels((0, 0), (0, 3))
        self.assertEqual(start_pixel, (0, 0))
        self.assertEqual(
            end_pixel, (480, 70)
        )  # Spans across 4 columns in the first row

        start_pixel, end_pixel = self.grid._grid_to_pixels((1, 1), (1, 2))
        self.assertEqual(start_pixel, (120, 70))  # 2nd row, 2nd column
        self.assertEqual(end_pixel, (360, 140))  # Spans across 2 columns

    def test_set_text_single_cell(self):
        """Test that text is correctly placed within a single grid cell."""
        self.grid.set_text((2, 1), "Test4", end=((2, 1)))

        # Check that draw_text was called with the correct pixel coordinates
        self.image_drawer.draw_text.assert_called_with(
            "Test4", (120, 140), end=(240, 210), font_name=None, anchor="lt"
        )

    def test_set_text_multiple_cells(self):
        """Test that text is correctly placed spanning multiple grid cells."""
        self.grid.set_text(
            (0, 0), "Test1", end=(0, 3), font_name="PixelSplitter-Bold", anchor="lt"
        )

        # Check that draw_text was called with the correct pixel coordinates
        self.image_drawer.draw_text.assert_called_with(
            "Test1", (0, 0), end=(480, 70), font_name="PixelSplitter-Bold", anchor="lt"
        )

    def test_set_text_different_rows(self):
        """Test text spanning across rows and columns."""
        self.grid.set_text(
            (1, 0), "TestMulticell", end=(2, 2), font_name="Roboto-Bold", anchor="lt"
        )

        # Check that draw_text was called with the correct pixel coordinates
        self.image_drawer.draw_text.assert_called_with(
            "TestMulticell",
            (0, 70),
            end=(360, 210),
            font_name="Roboto-Bold",
            anchor="lt",
        )


if __name__ == "__main__":
    unittest.main()
