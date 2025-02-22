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

    def _grid_to_pixels(self, start_grid, end_grid):
        """Convert grid coordinates (row, col) to pixel coordinates on the image.

        - start_grid: Tuple (row_start, col_start)
        - end_grid: Tuple (row_end, col_end)
        """
        x1 = int(start_grid[1] * self.cell_width + self.margin_x)
        y1 = int(start_grid[0] * self.cell_height + self.margin_y)
        x2 = int((end_grid[1] + 1) * self.cell_width - self.margin_x)
        y2 = int((end_grid[0] + 1) * self.cell_height - self.margin_y)
        return (x1, y1), (x2, y2)

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

    def set_text(self, start, text, end=None, font_name=None, anchor="lt", **kwargs):
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

        start_pixel, end_pixel = self.get_grid(start, end=end, convert_to_pixel=True)
        if anchor not in ["rs"]:
            self.image_drawer.draw_text(
                text,
                start_pixel,
                end=end_pixel,
                font_name=font_name,
                anchor=anchor,
                **kwargs,
            )
        else:
            self.image_drawer.draw_text(
                text,
                end_pixel,
                end=start_pixel,
                font_name=font_name,
                anchor=anchor,
                **kwargs,
            )

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
