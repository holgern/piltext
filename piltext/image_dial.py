import math

from PIL import Image

from .font_manager import FontManager
from .image_drawer import ImageDrawer


class ImageDial:
    """
    Create a dial (gauge) image representing a percentage using PIL, using the same
    drawing and font management logic as the rest of the codebase.
    """

    def __init__(
        self,
        percentage: float,
        font_manager: FontManager,
        size: int = 200,
        radius: int | None = None,
        bg_color: str = "white",
        fg_color: str = "#4CAF50",
        track_color: str = "#e0e0e0",
        thickness: int = 20,
        font_name: str | None = None,
        font_size: int | None = None,
        font_variation: str | None = None,
        show_needle: bool = True,
        show_ticks: bool = True,
        show_value: bool = True,
        start_angle: int = -135,
        end_angle: int = 135,
    ):
        self.percentage = max(0.0, min(1.0, percentage))
        self.font_manager = font_manager
        self.size = size
        self.radius = radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.track_color = track_color
        self.thickness = thickness
        self.font_name = font_name
        self.font_size = font_size
        self.font_variation = font_variation
        self.show_needle = show_needle
        self.show_ticks = show_ticks
        self.show_value = show_value
        self.start_angle = start_angle
        self.end_angle = end_angle

    def render(self) -> Image.Image:
        """
        Render the dial as a PIL Image.
        """
        # Create an image drawer with the specified size
        drawer = ImageDrawer(self.size, self.size, font_manager=self.font_manager)

        # Fill background
        drawer.draw.rectangle([0, 0, self.size, self.size], fill=self.bg_color)

        # Draw the dial elements
        self._draw_dial(drawer)

        # Return the final image
        return drawer.get_image()

    def _draw_dial(self, drawer: ImageDrawer):
        """
        Draw the dial on the image using the configured parameters.
        """
        # Calculate dimensions
        margin = self.thickness // 2 + 5
        center_x = self.size // 2
        center_y = self.size // 2

        # Use custom radius if provided, otherwise calculate based on size
        if self.radius is not None:
            radius = self.radius
        else:
            radius = (self.size - 2 * margin) // 2

        # Calculate bounding box for the dial based on radius
        bbox = [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ]

        # Angle definitions
        start_angle = self.start_angle
        end_angle = self.end_angle
        sweep = end_angle - start_angle

        # Draw track (background arc)
        drawer.draw.arc(
            bbox,
            start=start_angle,
            end=end_angle,
            fill=self.track_color,
            width=self.thickness,
        )

        # Draw foreground arc (percentage)
        if self.percentage > 0:
            arc_end = start_angle + self.percentage * sweep
            drawer.draw.arc(
                bbox,
                start=start_angle,
                end=arc_end,
                fill=self.fg_color,
                width=self.thickness,
            )

        # Draw needle
        if self.show_needle:
            needle_angle = start_angle + self.percentage * sweep
            self._draw_needle(drawer, center_x, center_y, radius, needle_angle)

        # Draw tick marks
        if self.show_ticks:
            self._draw_ticks(drawer, center_x, center_y, radius, start_angle, end_angle)

        # Draw percentage value in the center
        if self.show_value:
            value_text = f"{int(self.percentage * 100)}%"
            font_size = self.font_size or max(10, self.size // 10)
            try:
                drawer.draw_text(
                    value_text,
                    (center_x, center_y),
                    font_size=font_size,
                    font_name=self.font_name,
                    font_variation=self.font_variation,
                    fill="black",
                    anchor="mm",  # Center the text
                )
            except Exception:
                # If text drawing fails, continue without text
                pass

    def _draw_ticks(
        self,
        drawer: ImageDrawer,
        cx: int,
        cy: int,
        radius: int,
        start_angle: int,
        end_angle: int,
    ):
        """Draw tick marks around the dial."""
        # Draw major and minor ticks
        major_ticks = 5  # Number of major ticks (including start and end)
        minor_per_major = 4  # Number of minor ticks between major ticks

        sweep = end_angle - start_angle

        # Draw major ticks and labels
        for i in range(major_ticks):
            angle_rad = math.radians(start_angle + (i / (major_ticks - 1)) * sweep)

            # Tick coordinates - outer end
            outer_x = cx + int((radius + 5) * math.cos(angle_rad))
            outer_y = cy + int((radius + 5) * math.sin(angle_rad))

            # Tick coordinates - inner end
            inner_x = cx + int((radius - 10) * math.cos(angle_rad))
            inner_y = cy + int((radius - 10) * math.sin(angle_rad))

            # Draw major tick
            drawer.draw.line(
                [(outer_x, outer_y), (inner_x, inner_y)], fill="black", width=2
            )

            # Draw label
            label_value = int((i / (major_ticks - 1)) * 100)
            label_x = cx + int((radius + 20) * math.cos(angle_rad))
            label_y = cy + int((radius + 20) * math.sin(angle_rad))

            font_size = self.font_size or max(8, self.size // 20)
            try:
                drawer.draw_text(
                    str(label_value),
                    (label_x, label_y),
                    font_size=font_size,
                    font_name=self.font_name,
                    font_variation=self.font_variation,
                    fill="black",
                    anchor="mm",
                )
            except Exception:
                # If text drawing fails, continue without labels
                pass

        # Draw minor ticks
        total_segments = (major_ticks - 1) * minor_per_major
        for i in range(1, total_segments):
            if i % minor_per_major == 0:
                continue  # Skip positions where major ticks are

            angle_rad = math.radians(start_angle + (i / total_segments) * sweep)

            # Tick coordinates
            outer_x = cx + int((radius + 2) * math.cos(angle_rad))
            outer_y = cy + int((radius + 2) * math.sin(angle_rad))

            inner_x = cx + int((radius - 5) * math.cos(angle_rad))
            inner_y = cy + int((radius - 5) * math.sin(angle_rad))

            # Draw minor tick
            drawer.draw.line(
                [(outer_x, outer_y), (inner_x, inner_y)], fill="gray", width=1
            )

    def _draw_needle(
        self, drawer: ImageDrawer, cx: int, cy: int, radius: int, angle: float
    ):
        """Draw a needle pointing to the current value."""
        angle_rad = math.radians(angle)

        # Calculate needle coordinates
        needle_length = radius - self.thickness // 2 - 10
        needle_x = cx + int(needle_length * math.cos(angle_rad))
        needle_y = cy + int(needle_length * math.sin(angle_rad))

        # Draw needle line
        drawer.draw.line([(cx, cy), (needle_x, needle_y)], fill="red", width=3)

        # Draw needle pivot (center circle)
        pivot_radius = max(4, self.size // 30)
        drawer.draw.ellipse(
            [
                (cx - pivot_radius, cy - pivot_radius),
                (cx + pivot_radius, cy + pivot_radius),
            ],
            fill="black",
            outline="gray",
        )
