import os
import unittest

from piltext import FontManager, ImageDrawer


class TestImageDrawer(unittest.TestCase):
    def setUp(self):
        self.fontdirs = [
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
        ]
        self.font_manager = FontManager(fontdirs=self.fontdirs)
        self.image_drawer = ImageDrawer(100, 100, font_manager=self.font_manager)

    def test_draw_text_with_size_calculation(self):
        # Mock text size calculation and drawing
        xy = (0, 0)
        w, h, font_size = self.image_drawer.draw_text(
            "Test", xy, end=(100, 100), font_name="Roboto-Bold"
        )
        self.assertEqual(w, 100)
        self.assertEqual(h, 49)
        self.assertEqual(font_size, 51)


if __name__ == "__main__":
    unittest.main()
