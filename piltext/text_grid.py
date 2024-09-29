class TextGrid:
    def __init__(self, rows, cols, image_drawer):
        """Initialize the grid.

        - rows: Number of rows in the grid.
        - cols: Number of columns in the grid.
        - image_drawer: Instance of ImageDrawer to draw on.
        """
        self.rows = rows
        self.cols = cols
        self.image_drawer = image_drawer
        self.width, self.height = image_drawer.image_handler.image.size

        # Calculate the width and height of each grid cell
        self.cell_width = self.width // cols
        self.cell_height = self.height // rows

    def _grid_to_pixels(self, start_grid, end_grid):
        """Convert grid coordinates (row, col) to pixel coordinates on the image.

        - start_grid: Tuple (row_start, col_start)
        - end_grid: Tuple (row_end, col_end)
        """
        x1 = start_grid[1] * self.cell_width
        y1 = start_grid[0] * self.cell_height
        x2 = (end_grid[1] + 1) * self.cell_width  # +1 to include the entire end cell
        y2 = (end_grid[0] + 1) * self.cell_height
        return (x1, y1), (x2, y2)

    def set_text(self, start_grid, end_grid, text, font_name=None, **kwargs):
        """Place text on the image, spanning from start_grid to end_grid.

        - start_grid: Tuple (row_start, col_start)
        - end_grid: Tuple (row_end, col_end)
        - text: Text to display.
        - font_name: Optional font to use.
        """
        start_pixel, end_pixel = self._grid_to_pixels(start_grid, end_grid)
        self.image_drawer.draw_text(
            text, start_pixel, end=end_pixel, font_name=font_name, **kwargs
        )
