class TextGrid:
    def __init__(self, rows, cols, image_drawer, margin_x=0, margin_y=0):
        """Initialize the grid.

        - rows: Number of rows in the grid.
        - cols: Number of columns in the grid.
        - image_drawer: Instance of ImageDrawer to draw on.
        - margin_x: Horizontal margin (left & right) inside each cell.
        - margin_y: Vertical margin (top & bottom) inside each cell.
        """
        self.rows = rows
        self.cols = cols
        self.image_drawer = image_drawer
        self.width, self.height = image_drawer.image_handler.image.size

        # Store margins
        self.margin_x = margin_x
        self.margin_y = margin_y

        # Calculate the width and height of each grid cell
        self.cell_width = (self.width) / cols
        self.cell_height = (self.height) / rows

        # Calculate the drawable area inside each cell after applying margins
        self.inner_cell_width = self.cell_width - 2 * margin_x
        self.inner_cell_height = self.cell_height - 2 * margin_y

        # Dictionary to store merged cells
        self.merged_cells = {}
        self.grid2pixel = {}  # (row, col) => (x1, y1, x2, y2)

    def get_grid(self, start, end=None, convert_to_pixel=False):
        """Returns Grid cell or pixel coordinates.
        Args:
            start (tuple[int, int] | int): If a tuple, it represents (row, col)
                in the grid.
                If an integer, it refers to a merged cell index.
            end (tuple[int, int], optional): The bottom-right coordinate of a
                merged cell range.
                If None, the function determines the end position based on merged cells.
            convert_to_pixel boolean: If True the output is (x1, y1), (x2, y2),
                otherwise the output is start_grid, end_grid

        Notes:
            - If `start` is a tuple (row, col), the function checks if the cell is
              part of a merged group.
            - If `start` is an integer, it retrieves the corresponding
              merged cell coordinates.
        """
        if end is None and isinstance(start, tuple):
            row, col = start
            # Check if this cell is part of a merged group
            if (row, col) in self.merged_cells:
                start_grid, end_grid = self.merged_cells[(row, col)]
            else:
                start_grid, end_grid = (row, col), (row, col)
        elif end is None and isinstance(start, int):
            start_grid, end_grid = self.get_merged_cells_list()[start]
        else:
            start_grid = start
            end_grid = end
        if convert_to_pixel:
            return self._grid_to_pixels(start_grid, end_grid)
        return start_grid, end_grid

    def _grid_to_pixels_old(self, start_grid, end_grid):
        """Convert grid coordinates (row, col) to pixel coordinates on the image.

        - start_grid: Tuple (row_start, col_start)
        - end_grid: Tuple (row_end, col_end)
        """
        x1 = int(start_grid[1] * self.cell_width + self.margin_x)
        y1 = int(start_grid[0] * self.cell_height + self.margin_y)
        x2 = int((end_grid[1] + 1) * self.cell_width - self.margin_x)
        y2 = int((end_grid[0] + 1) * self.cell_height - self.margin_y)
        return (x1, y1), (x2, y2)

    def _grid_to_pixels(self, start_grid, end_grid):
        """Compute pixel coordinates for a grid region."""

        def get_or_compute_cell(row, col):
            if (row, col) not in self.grid2pixel:
                x1 = int(col * self.cell_width + self.margin_x)
                y1 = int(row * self.cell_height + self.margin_y)
                x2 = int((col + 1) * self.cell_width - self.margin_x)
                y2 = int((row + 1) * self.cell_height - self.margin_y)
                self.grid2pixel[(row, col)] = [x1, y1, x2, y2]
            return self.grid2pixel[(row, col)]

        x1s, y1s, x2s, y2s = [], [], [], []
        for row in range(start_grid[0], end_grid[0] + 1):
            for col in range(start_grid[1], end_grid[1] + 1):
                x1, y1, x2, y2 = get_or_compute_cell(row, col)
                x1s.append(x1)
                y1s.append(y1)
                x2s.append(x2)
                y2s.append(y2)

        return (min(x1s), min(y1s)), (max(x2s), max(y2s))

    def merge(self, start_grid, end_grid):
        """Merge multiple grid cells into one.

        - start_grid: Tuple (row_start, col_start)
        - end_grid: Tuple (row_end, col_end)
        """
        for row in range(start_grid[0], end_grid[0] + 1):
            for col in range(start_grid[1], end_grid[1] + 1):
                self.merged_cells[(row, col)] = (start_grid, end_grid)

    def merge_bulk(self, merge_list):
        """Merge multiple regions at once.

        - merge_list: List of tuples [((row_start, col_start), (row_end, col_end)), ...]
        """
        for start_grid, end_grid in merge_list:
            self.merge(start_grid, end_grid)

    def _get_cell_dimensions(self, start, end=None):
        """Get pixel width and height of a grid cell or merged cell."""
        (x1, y1), (x2, y2) = self.get_grid(start, end=end, convert_to_pixel=True)
        width = x2 - x1
        height = y2 - y1
        return (x1, y1), (x2, y2), width, height

    def set_text(
        self,
        start,
        text,
        end=None,
        font_name=None,
        font_variation=None,
        anchor="lt",
        **kwargs,
    ):
        """Place text within a grid cell or merged cell range.

        Args:
            start (tuple[int, int] | int): If a tuple, it represents (row, col)
                in the grid.
                If an integer, it refers to a merged cell index.
            text (str): The text to be displayed.
            end (tuple[int, int], optional): The bottom-right coordinate of a
                merged cell range.
                If None, the function determines the end position based on merged cells.
            font_name (str, optional): The font to use for rendering the text.
            anchor (str, optional): The text anchor position, e.g., "lt" (left-top) or
                "rs" (right-side).
            **kwargs: Additional keyword arguments for text rendering.

        Notes:
            - If `start` is a tuple (row, col), the function checks if the cell is
              part of a merged group.
            - If `start` is an integer, it retrieves the corresponding
              merged cell coordinates.
            - The text position is determined based on the anchor.
        """
        (x1, y1), (x2, y2), width, height = self._get_cell_dimensions(start, end=end)

        if anchor not in ["rs"]:
            return self.image_drawer.draw_text(
                text,
                (x1, y1),
                end=(x2, y2),
                font_name=font_name,
                font_variation=font_variation,
                anchor=anchor,
                **kwargs,
            )
        else:
            return self.image_drawer.draw_text(
                text,
                (x2, y2),
                end=(x1, y1),
                font_name=font_name,
                font_variation=font_variation,
                anchor=anchor,
                **kwargs,
            )

    def get_dimensions(self, start, end=None, verbose=False):
        """Print and return the pixel dimensions of a grid or merged cell.

        Args:
            start (tuple[int, int] | int): Grid cell coordinates (row, col) or index.
            end (tuple[int, int], optional): Optional end for merged cell ranges.

        Returns:
            dict: {
                'start': (row_start, col_start),
                'end': (row_end, col_end),
                'x': top-left x,
                'y': top-left y,
                'width': pixel: width,
                'height': pixel height
            }
        """
        start_grid, end_grid = self.get_grid(start, end)
        (x1, y1), (x2, y2) = self.get_grid(start_grid, end_grid, convert_to_pixel=True)
        width = x2 - x1
        height = y2 - y1
        if verbose:
            print(f"Grid cell from {start_grid} to {end_grid}")
            print(f"Pixel coords: (x1={x1}, y1={y1}) to (x2={x2}, y2={y2})")
            print(f"Width: {width}px, Height: {height}px")

        return {
            "start": start_grid,
            "end": end_grid,
            "x": x1,
            "y": y1,
            "width": width,
            "height": height,
        }

    def modify_grid2pixel(self, start, d_x1=0, d_y1=0, d_x2=0, d_y2=0):
        """Modify a cell's pixel region by expanding/shrinking width/height.

        Args:
            start (tuple[int, int] | int): Starting grid cell or merged cell index.
            d_x1 (int): Pixels to expand (positive) or shrink (negative) width-wise.
            d_y1 (int): Pixels to expand (positive) or shrink (negative) width-wise.
            d_x2 (int): Pixels to expand (positive) or shrink (negative) width-wise.
            d_y2 (int): Pixels to expand (positive) or shrink (negative) width-wise.
        """
        start_grid, end_grid = self.get_grid(start, end=None)

        for row in range(start_grid[0], end_grid[0] + 1):
            for col in range(start_grid[1], end_grid[1] + 1):
                if (row, col) not in self.grid2pixel:
                    continue

                x1, y1, x2, y2 = self.grid2pixel[(row, col)]

                # Modify current cell
                x1 += d_x1
                x2 += d_x2
                y1 += d_y1
                y2 += d_y2
                self.grid2pixel[(row, col)] = [x1, y1, x2, y2]

    def modify_row_height(self, row, delta_y1=0, delta_y2=0):
        """
        Modify the top (y1) and/or bottom (y2) of all cells in a given row.

        Args:
            row (int): Row index to adjust.
            delta_y1 (int): Pixels to adjust the top (y1). Positive moves down.
            delta_y2 (int): Pixels to adjust the bottom (y2). Positive moves down.
        """
        if delta_y1 == 0 and delta_y2 == 0:
            return

        modified = set()

        for col in range(self.cols):
            key = (row, col)
            if key not in self.grid2pixel:
                continue

            merged_start, merged_end = self.get_grid(key)
            merged_key = (merged_start, merged_end)

            if merged_key in modified:
                continue  # Already modified

            self.modify_grid2pixel(
                merged_start,
                d_y1=delta_y1 if merged_start[0] == row else 0,
                d_y2=delta_y2 if merged_end[0] == row else 0,
            )
            modified.add(merged_key)

    def set_text_list(self, text_list):
        """Set text in multiple cells at once.

        - text_list: List of dictionaries, each containing:
            - "start": Tuple (row, col) indicating the starting grid position.
            - "text": The text to place in the cell.
            - Additional optional parameters for text formatting.
        """
        for text in text_list:
            start = text.pop("start")
            text_str = text.pop("text")
            self.set_text(start, text_str, **text)

    def paste_image(self, start, image, end=None, anchor="lt", **kwargs):
        """Place image within a grid cell or merged cell range.

        Args:
            start (tuple[int, int] | int): If a tuple, it represents (row, col)
                in the grid.
                If an integer, it refers to a merged cell index.
            image: The image to be displayed.
            end (tuple[int, int], optional): The bottom-right coordinate of a
                merged cell range.
                If None, the function determines the end position based on merged cells.
            anchor (str, optional): The image anchor position, e.g., "lt" (left-top) or
                "rs" (right-side).

            **kwargs: Additional keyword arguments for text rendering.

        Notes:
            - If `start` is a tuple (row, col), the function checks if the cell is
              part of a merged group.
            - If `start` is an integer, it retrieves the corresponding
              merged cell coordinates.
            - The text position is determined based on the anchor.
        """
        start_pixel, end_pixel = self.get_grid(start, end=end, convert_to_pixel=True)
        if anchor in ["rs"]:
            box = (end_pixel[0] - image.width, end_pixel[1] - image.height)
        else:
            box = (start_pixel[0], start_pixel[1])
        self.image_drawer.paste(image, box=box, **kwargs)

    def get_merged_cells(self):
        """Returns a dictionary of merged cells."""
        merged_dict = {}
        for cell, merged_range in self.merged_cells.items():
            if merged_range not in merged_dict.values():
                merged_dict[cell] = merged_range
        return merged_dict

    def get_merged_cells_list(self):
        """Returns a list of merged cells."""
        merged_list = []
        merged_dict = {}
        for cell, merged_range in self.merged_cells.items():
            if merged_range not in merged_dict.values():
                merged_dict[cell] = merged_range
                merged_list.append(merged_range)
        return merged_list

    def print_grid(self):
        """Prints a visual representation of the merged grid."""
        grid_display = [["." for _ in range(self.cols)] for _ in range(self.rows)]
        cell_index = 0
        for (row, col), (start, end) in self.merged_cells.items():
            if (row, col) == start:  # Only mark the top-left corner of merged regions
                grid_display[row][col] = f"{cell_index}"
                cell_index += 1
            elif len(end) < 2:
                continue
            elif end[0] >= len(grid_display):
                continue
            elif end[1] >= len(grid_display[end[0]]):
                continue
            else:
                grid_display[end[0]][end[1]] = f"{cell_index - 1}"

        print("\nGrid Layout:")
        row_index = 0
        col_index = 0
        for row in grid_display:
            col_row = " "
            line_row = "-"
            for _ in row:
                col_row += f" {col_index}"
                line_row += "--"
                col_index += 1
            if row_index == 0:
                print(col_row)
                print(line_row)
            print(f"{row_index}|" + " ".join(row))
            row_index += 1

    def draw_grid_borders(self, color="gray", width=1):
        """Draw borders around all visible grid cells
        (respects merged and resized cells)."""
        drawn = set()
        for row in range(self.rows):
            for col in range(self.cols):
                key = (row, col)
                if key in drawn:
                    continue
                # Get the full merged region
                start_grid, end_grid = self.get_grid(key)
                # Avoid drawing multiple times for merged regions
                for r in range(start_grid[0], end_grid[0] + 1):
                    for c in range(start_grid[1], end_grid[1] + 1):
                        drawn.add((r, c))
                # Get pixel coords
                (x1, y1), (x2, y2) = self.get_grid(
                    start_grid, end_grid, convert_to_pixel=True
                )
                # Draw rectangle
                self.image_drawer.draw.rectangle(
                    [(x1, y1), (x2, y2)], outline=color, width=width
                )

    def get_required_row_height_for_text(
        self, start, text, end=None, font_name=None, font_variation=None, **kwargs
    ):
        """
        Calculates the pixel height required to display `text` in one line
        across a full row.

        Args:
            start (tuple[int, int] | int): If a tuple, it represents (row, col)
                in the grid.
                If an integer, it refers to a merged cell index.
            end (tuple[int, int], optional): The bottom-right coordinate of a
                merged cell range.
                If None, the function determines the end position based on
                merged cells.
            text (str): Text to measure.
            font_name (str, optional): Font name to use.
            font_variation (str, optional): Font variation/style.
            **kwargs: Additional arguments passed to draw_text (e.g., font_size).

        Returns:
            int: Required pixel height.
        """
        if not text:
            return 0

        # Get horizontal start and end pixel coordinates for the full row
        (x1, y1), (x2, y2) = self.get_grid(start, end, convert_to_pixel=True)
        max_width = x2 - x1

        # Binary search for max font size that fits within the row width
        min_font, max_font = 4, 300
        best_h = 0
        while min_font <= max_font:
            mid_font = (min_font + max_font) // 2
            w, h, _ = self.image_drawer.draw_text(
                text,
                (x1, y1),
                end=(x2, y2),
                font_name=font_name,
                font_variation=font_variation,
                font_size=mid_font,
                anchor="lt",
                measure_only=True,
                **kwargs,
            )
            if w <= max_width:
                best_h = h
                min_font = mid_font + 1
            else:
                max_font = mid_font - 1

        # Return final needed height including top & bottom margins
        return best_h + 2 * self.margin_y
