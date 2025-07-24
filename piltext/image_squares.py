import math

from PIL import Image

from .font_manager import FontManager
from .image_drawer import ImageDrawer


class ImageSquares:
    """
    Create a visualization of squares representing a percentage using PIL,
    showing the specified portion of maximum squares.
    """

    def __init__(
        self,
        percentage: float,
        font_manager: FontManager,
        max_squares: int = 100,
        size: int = 200,
        bg_color: str = "white",
        fg_color: str = "#4CAF50",
        empty_color: str = "#e0e0e0",
        gap: int = 2,
        rows: int | None = None,
        columns: int | None = None,
        border_width: int = 1,
        border_color: str = "#cccccc",
        show_partial: bool = True,
    ):
        self.percentage = max(0.0, min(1.0, percentage))
        self.font_manager = font_manager
        self.max_squares = max_squares
        self.size = size
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.empty_color = empty_color
        self.gap = gap
        self.border_width = border_width
        self.border_color = border_color
        self.show_partial = show_partial

        # Calculate the number of rows and columns based on max_squares
        # If not specified, try to make it as square as possible
        if rows is not None and columns is not None:
            self.rows = rows
            self.columns = columns
        elif rows is not None:
            self.rows = rows
            self.columns = math.ceil(max_squares / rows)
        elif columns is not None:
            self.columns = columns
            self.rows = math.ceil(max_squares / columns)
        else:
            # Make it as square as possible
            self.columns = math.ceil(math.sqrt(max_squares))
            self.rows = math.ceil(max_squares / self.columns)

        # Calculate the square size based on the overall size and grid dimensions
        self.square_size = (self.size - ((self.columns + 1) * self.gap)) // self.columns

    def render(self) -> Image.Image:
        """
        Render the squares visualization as a PIL Image.
        """
        # Calculate the actual width and height needed based on number of squares
        # and their size with gaps
        actual_width = (self.square_size * self.columns) + (
            (self.columns + 1) * self.gap
        )
        actual_height = (self.square_size * self.rows) + ((self.rows + 1) * self.gap)

        # Add space at bottom for percentage value if showing
        value_height = 0
        total_height = actual_height + value_height

        # Create an image drawer with the calculated dimensions
        drawer = ImageDrawer(actual_width, total_height, font_manager=self.font_manager)

        # Fill background
        drawer.draw.rectangle([0, 0, actual_width, total_height], fill=self.bg_color)

        # Draw the squares
        self._draw_squares(drawer)

        # Return the final image
        return drawer.get_image()

    def _draw_squares(self, drawer: ImageDrawer):
        """
        Draw the squares on the image using the configured parameters.
        """
        # Calculate how many squares should be filled based on percentage
        filled_squares = self.percentage * self.max_squares
        full_squares = math.floor(filled_squares)
        partial_square_value = filled_squares - full_squares

        # Draw all the squares
        for i in range(self.rows):
            for j in range(self.columns):
                # Calculate the square index
                index = i * self.columns + j

                # Skip if we've exceeded max_squares
                if index >= self.max_squares:
                    break

                # Calculate position
                x = self.gap + j * (self.square_size + self.gap)
                y = self.gap + i * (self.square_size + self.gap)

                # Determine fill color
                if index < full_squares:
                    fill_color = self.fg_color
                    fill_percentage = 1.0
                elif (
                    index == full_squares
                    and partial_square_value > 0
                    and self.show_partial
                ):
                    fill_color = self.fg_color
                    fill_percentage = partial_square_value
                else:
                    fill_color = self.empty_color
                    fill_percentage = 0.0

                # Draw the square
                if fill_percentage == 1.0:
                    # Draw a complete square
                    drawer.draw.rectangle(
                        [x, y, x + self.square_size, y + self.square_size],
                        fill=fill_color,
                        outline=self.border_color if self.border_width > 0 else None,
                        width=self.border_width,
                    )
                elif fill_percentage > 0:
                    # Draw empty square
                    drawer.draw.rectangle(
                        [x, y, x + self.square_size, y + self.square_size],
                        fill=self.empty_color,
                        outline=self.border_color if self.border_width > 0 else None,
                        width=self.border_width,
                    )

                    # Draw partial filled square (fill from left to right)
                    filled_width = int(self.square_size * fill_percentage)
                    drawer.draw.rectangle(
                        [
                            x + self.border_width,
                            y,
                            x + filled_width,
                            y + self.square_size - self.border_width,
                        ],
                        fill=fill_color,
                        outline=None,
                    )
                else:
                    # Draw an empty square
                    drawer.draw.rectangle(
                        [x, y, x + self.square_size, y + self.square_size],
                        fill=self.empty_color,
                        outline=self.border_color if self.border_width > 0 else None,
                        width=self.border_width,
                    )
