import unittest
from unittest.mock import patch

from PIL import Image

from piltext import ImageHandler


class TestImageHandler(unittest.TestCase):
    def setUp(self):
        self.image_handler = ImageHandler(100, 100)

    def test_initialize_image(self):
        self.assertIsInstance(self.image_handler.image, Image.Image)
        self.assertEqual(self.image_handler.image.size, (100, 100))

    def test_change_size(self):
        self.image_handler.change_size(200, 200)
        self.assertEqual(self.image_handler.image.size, (200, 200))

    @patch("PIL.Image.Image.rotate")
    @patch("PIL.ImageOps.mirror")
    def test_apply_transformations(self, mock_mirror, mock_rotate):
        self.image_handler.apply_transformations(mirror=True, orientation=90)
        mock_rotate.assert_called_once()
        mock_mirror.assert_called_once()

    @patch("PIL.ImageOps.invert")
    def test_apply_transformations_inverted(self, mock_invert):
        self.image_handler.apply_transformations(inverted=True)
        mock_invert.assert_called_once()

    def test_show_with_title(self):
        with patch.object(self.image_handler.image, "show") as mock_show:
            self.image_handler.show(title="Test Title")
            mock_show.assert_called_once()

    def test_show_without_title(self):
        with patch.object(self.image_handler.image, "show") as mock_show:
            self.image_handler.show()
            mock_show.assert_called_once()

    def test_show_with_title_fallback(self):
        with patch.object(
            self.image_handler.image, "show", side_effect=[TypeError, None]
        ):
            self.image_handler.show(title="Test Title")

    def test_paste_with_box(self):
        source_img = Image.new("RGB", (50, 50), "red")
        with patch.object(self.image_handler.image, "paste") as mock_paste:
            self.image_handler.paste(source_img, box=(10, 10))
            mock_paste.assert_called_once_with(source_img, box=(10, 10), mask=None)

    def test_paste_with_mask(self):
        source_img = Image.new("RGB", (50, 50), "red")
        mask_img = Image.new("L", (50, 50), 128)
        with patch.object(self.image_handler.image, "paste") as mock_paste:
            self.image_handler.paste(source_img, mask=mask_img)
            mock_paste.assert_called_once_with(source_img, box=None, mask=mask_img)


if __name__ == "__main__":
    unittest.main()
