import os
import unittest

from piltext import FontManager, ImageDrawer


class TestImageDrawer(unittest.TestCase):
    def setUp(self):
        self.fontdirs = [
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
        ]
        self.font_manager = FontManager(fontdirs=self.fontdirs)
        self.image_drawer = ImageDrawer(264, 127, font_manager=self.font_manager)

    def test_draw_text_with_size_calculation(self):
        # Mock text size calculation and drawing
        xy = (5, 16)
        w, h, font_size = self.image_drawer.draw_text(
            "12345 abcdefg", xy, end=(254, 16.55), font_name="Roboto-Bold", anchor="lt"
        )
        self.assertIn(w, [7, 11])
        self.assertIn(h, [1, 2])
        self.assertEqual(font_size, 1)
        # Mock text size calculation and drawing
        xy = (5, 16)
        w, h, font_size = self.image_drawer.draw_text(
            "12345 abcdefg", xy, end=(254, 25), font_name="Roboto-Bold", anchor="lt"
        )
        self.assertIn(w, [47, 48])
        self.assertEqual(h, 9)
        self.assertEqual(font_size, 7)


if __name__ == "__main__":
    unittest.main()
