"""
Grid-based text layout for images.

This module provides the TextGrid class for creating and managing a grid-based
layout system on images. It enables precise text and image placement within
cells, supports cell merging, and provides utilities for text sizing and
positioning.

Examples
--------
Create a 3x3 grid and add text to cells:

>>> from piltext import ImageDrawer, ImageHandler, TextGrid
>>> ih = ImageHandler(1200, 800, background_color='white')
>>> drawer = ImageDrawer(ih)
>>> grid = TextGrid(rows=3, cols=3, image_drawer=drawer, margin_x=10, margin_y=10)
>>> grid.set_text((0, 0), "Top Left", font_name="Arial", anchor="lt")
>>> grid.set_text((1, 1), "Center", font_name="Arial", anchor="mm")
>>> ih.save("grid_example.png")

Merge cells and add text:

>>> grid.merge((0, 0), (0, 2))  # Merge top row
>>> grid.set_text((0, 0), "Header Text", font_name="Arial", anchor="mm")
"""


class TextGrid:
    def __init__(self, rows, cols, image_drawer, margin_x=0, margin_y=0):
        """
        Initialize a text grid layout.

        Parameters
        ----------
        rows : int
            Number of rows in the grid.
        cols : int
            Number of columns in the grid.
        image_drawer : ImageDrawer
            Instance of ImageDrawer to draw on.
        margin_x : int, optional
            Horizontal margin (left & right) inside each cell in pixels.
            Default is 0.
        margin_y : int, optional
            Vertical margin (top & bottom) inside each cell in pixels.
            Default is 0.

        Attributes
        ----------
        rows : int
            Number of rows in the grid.
        cols : int
            Number of columns in the grid.
        cell_width : float
            Width of each cell in pixels.
        cell_height : float
            Height of each cell in pixels.
        inner_cell_width : float
            Drawable width inside each cell after margins.
        inner_cell_height : float
            Drawable height inside each cell after margins.
        merged_cells : dict
            Dictionary mapping cell coordinates to merged regions.

        Examples
        --------
        Create a 2x3 grid with margins:

        >>> from piltext import ImageHandler, ImageDrawer, TextGrid
        >>> ih = ImageHandler(600, 400, background_color='white')
        >>> drawer = ImageDrawer(ih)
        >>> grid = TextGrid(2, 3, drawer, margin_x=10, margin_y=5)
        >>> grid.cell_width
        200.0
        >>> grid.cell_height
        200.0
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

    def _get_or_compute_cell(self, row, col):
        if (row, col) not in self.grid2pixel:
            x1 = int(col * self.cell_width + self.margin_x)
            y1 = int(row * self.cell_height + self.margin_y)
            x2 = int((col + 1) * self.cell_width - self.margin_x)
            y2 = int((row + 1) * self.cell_height - self.margin_y)
            self.grid2pixel[(row, col)] = [x1, y1, x2, y2]
        return self.grid2pixel[(row, col)]

    def get_grid(self, start, end=None, convert_to_pixel=False):
        """Returns Grid cell or pixel coordinates.

        Parameters
        ----------
        start : tuple[int, int] or int
            If a tuple, it represents (row, col) in the grid.
            If an integer, it refers to a merged cell index.
        end : tuple[int, int], optional
            The bottom-right coordinate of a merged cell range.
            If None, the function determines the end position based on merged cells.
        convert_to_pixel : bool, default=False
            If True the output is (x1, y1), (x2, y2), otherwise the output is
            start_grid, end_grid.

        Returns
        -------
        tuple
            If convert_to_pixel is False: (start_grid, end_grid) as grid coordinates.
            If convert_to_pixel is True: ((x1, y1), (x2, y2)) as pixel coordinates.

        Raises
        ------
        ValueError
            If grid coordinates cannot be determined from start and end.
        IndexError
            If merged cell index is out of range.

        Notes
        -----
        - If `start` is a tuple (row, col), the function checks if the cell is
          part of a merged group.
        - If `start` is an integer, it retrieves the corresponding
          merged cell coordinates.
        """
        start_grid, end_grid = None, None

        if end is not None:
            start_grid = start
            end_grid = end
        elif isinstance(start, tuple) and len(start) == 2:
            row, col = start
            if (row, col) in self.merged_cells:
                start_grid, end_grid = self.merged_cells[(row, col)]
            else:
                start_grid, end_grid = start, start
        elif isinstance(start, int):
            try:
                start_grid, end_grid = self.get_merged_cells_list()[start]
            except IndexError as e:
                raise IndexError(f"Merged cell index {start} is out of range.") from e

        if start_grid is None or end_grid is None:
            raise ValueError(
                f"Could not determine grid coordinates for start={start}, end={end}"
            )

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
        """
        Compute pixel coordinates for a grid region.

        Parameters
        ----------
        start_grid : tuple of int
            Starting grid position (row, col).
        end_grid : tuple of int
            Ending grid position (row, col).

        Returns
        -------
        tuple
            ((x1, y1), (x2, y2)) representing top-left and bottom-right
            pixel coordinates.
        """
        x1s, y1s, x2s, y2s = [], [], [], []
        for row in range(start_grid[0], end_grid[0] + 1):
            for col in range(start_grid[1], end_grid[1] + 1):
                x1, y1, x2, y2 = self._get_or_compute_cell(row, col)
                x1s.append(x1)
                y1s.append(y1)
                x2s.append(x2)
                y2s.append(y2)

        return (min(x1s), min(y1s)), (max(x2s), max(y2s))

    def merge(self, start_grid, end_grid):
        """
        Merge multiple grid cells into one region.

        Parameters
        ----------
        start_grid : tuple of int
            Starting grid position (row, col).
        end_grid : tuple of int
            Ending grid position (row, col).

        Examples
        --------
        Merge cells to create a header spanning the top row:

        >>> grid.merge((0, 0), (0, 2))  # Merge first row, columns 0-2
        """
        for row in range(start_grid[0], end_grid[0] + 1):
            for col in range(start_grid[1], end_grid[1] + 1):
                self.merged_cells[(row, col)] = (start_grid, end_grid)

    def merge_bulk(self, merge_list):
        """
        Merge multiple cell regions at once.

        Parameters
        ----------
        merge_list : list of tuple
            List of merge specifications, where each element is a tuple
            ((row_start, col_start), (row_end, col_end)).

        Examples
        --------
        Merge multiple regions in one call:

        >>> merges = [
        ...     ((0, 0), (0, 2)),  # Top row
        ...     ((1, 0), (2, 0))   # Left column
        ... ]
        >>> grid.merge_bulk(merges)
        """
        for start_grid, end_grid in merge_list:
            self.merge(start_grid, end_grid)

    def _get_cell_dimensions(self, start, end=None):
        """
        Get pixel width and height of a grid cell or merged cell.

        Args:
            start (tuple[int, int] | int): Grid cell coordinates (row, col) or index.
                Must not be None.
            end (tuple[int, int], optional): Optional end for merged cell ranges.

        Returns:
            ((int, int), (int, int), int, int):
                - (x1, y1): top-left pixel coordinates
                - (x2, y2): bottom-right pixel coordinates
                - width: pixel width
                - height: pixel height
        Raises:
            ValueError: If start is None.
        """
        if start is None:
            raise ValueError("start cannot be None in _get_cell_dimensions")
        (x1, y1), (x2, y2) = self.get_grid(start, end=end, convert_to_pixel=True)
        width = x2 - x1
        height = y2 - y1
        return (x1, y1), (x2, y2), width, height

    def _calculate_anchor_position(self, x1, y1, x2, y2, anchor):
        """Calculate the actual position for text based on anchor and bounding box.

        PIL's text anchor expects the xy parameter to be at the anchor point.
        For example, if anchor="mm" (middle-middle), xy should be the center.

        Args:
            x1, y1: Top-left corner of bounding box
            x2, y2: Bottom-right corner of bounding box
            anchor: Two-character anchor string (e.g., "lt", "mm", "rb")

        Returns:
            (x, y): The position to pass to draw.text()
        """
        if len(anchor) != 2:
            anchor = "lt"

        # Horizontal position
        h_anchor = anchor[1]  # second char: l=left, m=middle, r=right
        if h_anchor == "l":
            x = x1
        elif h_anchor == "m":
            x = (x1 + x2) / 2
        elif h_anchor == "r":
            x = x2
        else:
            x = x1

        # Vertical position
        v_anchor = anchor[0]  # first char: t=top, m=middle, b=bottom, s=baseline
        if v_anchor == "t":
            y = y1
        elif v_anchor == "m":
            y = (y1 + y2) / 2
        elif v_anchor == "b" or v_anchor == "s":
            y = y2
        else:
            y = y1

        return (x, y)

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
        """
        Place text within a grid cell or merged cell range.

        Parameters
        ----------
        start : tuple of int or int
            If a tuple, represents (row, col) in the grid.
            If an integer, refers to a merged cell index. Must not be None.
        text : str
            The text to be displayed.
        end : tuple of int, optional
            The bottom-right coordinate of a merged cell range.
            If None, determined from merged cells.
        font_name : str, optional
            The font to use for rendering the text.
        font_variation : str, optional
            Font variation (e.g., 'Bold', 'Italic').
        anchor : str, optional
            The text anchor position (e.g., 'lt', 'mm', 'rs'). Default is 'lt'.
        **kwargs
            Additional keyword arguments for text rendering.

        Raises
        ------
        ValueError
            If start is None.

        Notes
        -----
        - If `start` is a tuple (row, col), the function checks if the cell is
          part of a merged group.
        - If `start` is an integer, it retrieves the corresponding
          merged cell coordinates.
        - The text position is determined based on the anchor.
        """
        if start is None:
            raise ValueError("start cannot be None in set_text")
        (x1, y1), (x2, y2), width, height = self._get_cell_dimensions(start, end=end)

        # Calculate the actual position based on anchor
        position = self._calculate_anchor_position(x1, y1, x2, y2, anchor)

        return self.image_drawer.draw_text(
            text,
            position,
            end=(x2, y2),
            font_name=font_name,
            font_variation=font_variation,
            anchor=anchor,
            **kwargs,
        )

    def get_dimensions(self, start, end=None, verbose=False):
        """
        Print and return the pixel dimensions of a grid or merged cell.

        Parameters
        ----------
        start : tuple of int or int
            Grid cell coordinates (row, col) or merged cell index.
        end : tuple of int, optional
            Optional end for merged cell ranges.
        verbose : bool, optional
            If True, print dimension information. Default is False.

        Returns
        -------
        dict
            Dictionary containing:

            - 'start': tuple, starting grid position (row, col)
            - 'end': tuple, ending grid position (row, col)
            - 'x': int, top-left x coordinate
            - 'y': int, top-left y coordinate
            - 'width': int, pixel width
            - 'height': int, pixel height
        """
        start_grid, end_grid = self.get_grid(start, end)
        (x1, y1), (x2, y2), width, height = self._get_cell_dimensions(
            start_grid, end_grid
        )
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
        """
        Modify a cell's pixel region by adjusting its boundaries.

        Parameters
        ----------
        start : tuple of int or int
            Starting grid cell or merged cell index.
        d_x1 : int, optional
            Pixels to adjust the left boundary. Positive expands,
            negative shrinks. Default is 0.
        d_y1 : int, optional
            Pixels to adjust the top boundary. Positive expands,
            negative shrinks. Default is 0.
        d_x2 : int, optional
            Pixels to adjust the right boundary. Positive expands,
            negative shrinks. Default is 0.
        d_y2 : int, optional
            Pixels to adjust the bottom boundary. Positive expands,
            negative shrinks. Default is 0.
        """
        start_grid, end_grid = self.get_grid(start, end=None)

        # Apply vertical changes
        if d_y1 != 0:
            row = start_grid[0]
            for col in range(start_grid[1], end_grid[1] + 1):
                self._get_or_compute_cell(row, col)[1] -= d_y1
        if d_y2 != 0:
            row = end_grid[0]
            for col in range(start_grid[1], end_grid[1] + 1):
                self._get_or_compute_cell(row, col)[3] += d_y2

        # Apply horizontal changes
        if d_x1 != 0:
            col = start_grid[1]
            for row in range(start_grid[0], end_grid[0] + 1):
                self._get_or_compute_cell(row, col)[0] -= d_x1
        if d_x2 != 0:
            col = end_grid[1]
            for row in range(start_grid[0], end_grid[0] + 1):
                self._get_or_compute_cell(row, col)[2] += d_x2

    def modify_row_height(self, row, delta_y1=0, delta_y2=0):
        """
        Modify the top (y1) and/or bottom (y2) of all cells in a given row.

        Parameters
        ----------
        row : int
            Row index to adjust.
        delta_y1 : int, optional
            Pixels to adjust the top (y1). Positive moves down. Default is 0.
        delta_y2 : int, optional
            Pixels to adjust the bottom (y2). Positive moves down. Default is 0.
        """
        if delta_y1 == 0 and delta_y2 == 0:
            return

        modified = set()

        for col in range(self.cols):
            key = (row, col)
            # if key not in self.grid2pixel:
            #    continue

            merged_start, merged_end = self.get_grid(key)
            merged_key = (merged_start, merged_end)

            if merged_key in modified:
                continue  # Already modified

            self.modify_grid2pixel(
                merged_start,
                d_y1=-delta_y1 if merged_start[0] == row else 0,
                d_y2=delta_y2 if merged_end[0] == row else 0,
            )
            modified.add(merged_key)

    def set_text_list(self, text_list):
        """
        Set text in multiple cells at once.

        Parameters
        ----------
        text_list : list of dict
            List of text specifications, where each dictionary contains:
            - 'start': tuple (row, col) for cell position
            - 'text': str, the text to display
            - Additional optional parameters for text formatting

        Examples
        --------
        Add text to multiple cells:

        >>> texts = [
        ...     {'start': (0, 0), 'text': 'Header', 'font_name': 'Arial'},
        ...     {'start': (1, 0), 'text': 'Row 1', 'anchor': 'mm'}
        ... ]
        >>> grid.set_text_list(texts)
        """
        for text in text_list:
            start = text.pop("start")
            text_str = text.pop("text")
            self.set_text(start, text_str, **text)

    def paste_image(self, start, image, end=None, anchor="lt", **kwargs):
        """
        Place image within a grid cell or merged cell range.

        Parameters
        ----------
        start : tuple of int or int
            If a tuple, represents (row, col) in the grid.
            If an integer, refers to a merged cell index.
        image : PIL.Image.Image
            The image to be displayed.
        end : tuple of int, optional
            The bottom-right coordinate of a merged cell range.
            If None, determined from merged cells.
        anchor : str, optional
            The image anchor position (e.g., 'lt', 'rs'). Default is 'lt'.
        **kwargs
            Additional keyword arguments for image pasting.

        Notes
        -----
        - If `start` is a tuple (row, col), the function checks if the cell is
          part of a merged group.
        - If `start` is an integer, it retrieves the corresponding
          merged cell coordinates.
        - The image position is determined based on the anchor.
        """
        start_pixel, end_pixel = self.get_grid(start, end=end, convert_to_pixel=True)
        if anchor in ["rs"]:
            box = (end_pixel[0] - image.width, end_pixel[1] - image.height)
        else:
            box = (start_pixel[0], start_pixel[1])
        self.image_drawer.paste(image, box=box, **kwargs)

    def get_merged_cells(self):
        """
        Get a dictionary of merged cells.

        Returns
        -------
        dict
            Dictionary mapping cell coordinates to their merged region
            boundaries ((start_row, start_col), (end_row, end_col)).
        """
        merged_dict = {}
        for cell, merged_range in self.merged_cells.items():
            if merged_range not in merged_dict.values():
                merged_dict[cell] = merged_range
        return merged_dict

    def get_merged_cells_list(self):
        """
        Get a list of all merged cell regions.

        Returns
        -------
        list of tuple
            List of merged regions, where each element is
            ((start_row, start_col), (end_row, end_col)).
        """
        merged_list = []
        merged_dict = {}
        for cell, merged_range in self.merged_cells.items():
            if merged_range not in merged_dict.values():
                merged_dict[cell] = merged_range
                merged_list.append(merged_range)
        return merged_list

    def print_grid(self):
        """
        Print a visual representation of the grid with merged cells.

        Notes
        -----
        Displays a text-based visualization showing cell indices and
        merged regions. Useful for debugging grid layouts.
        """
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
        """
        Draw borders around all grid cells.

        Parameters
        ----------
        color : str, optional
            Border color. Default is 'gray'.
        width : int, optional
            Border width in pixels. Default is 1.

        Notes
        -----
        Respects merged and resized cells, drawing borders around the
        actual visible cell boundaries.
        """
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
        Calculate the pixel height required to display text in one line.

        Parameters
        ----------
        start : tuple of int or int
            If a tuple, represents (row, col) in the grid.
            If an integer, refers to a merged cell index.
        text : str
            Text to measure.
        end : tuple of int, optional
            The bottom-right coordinate of a merged cell range.
            If None, determined from merged cells.
        font_name : str, optional
            Font name to use.
        font_variation : str, optional
            Font variation/style.
        **kwargs
            Additional arguments passed to draw_text (e.g., font_size).

        Returns
        -------
        int
            Required pixel height for the text to fit in one line
            across the full row.
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
