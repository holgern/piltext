# piltext

[![codecov](https://codecov.io/gh/holgern/piltext/graph/badge.svg?token=VyIU0ZxwpD)](https://codecov.io/gh/holgern/piltext)
[![PyPi Version](https://img.shields.io/pypi/v/piltext.svg)](https://pypi.python.org/pypi/piltext/)

A Python library for creating PNG images from text using Pillow. Features include
precise text positioning, automatic font scaling, grid layouts, and percentage
visualizations (dials and waffle charts).

## Features

- 🎨 **Text Rendering** - Draw text with customizable fonts, sizes, colors, and styles
- 📐 **Auto-Fit Scaling** - Automatically scale text to fit within bounding boxes
- ⚓ **Anchor Positioning** - Precise text alignment (left/center/right,
  top/middle/bottom)
- 🔤 **Font Management** - Load local fonts or download from Google Fonts
- 📊 **Grid Layouts** - Create multi-cell grids with merged cells
- 📈 **Visualizations** - Built-in dial gauges and waffle charts for percentages
- ⚙️ **TOML Configuration** - Define complex layouts with simple config files
- 🖼️ **Image Transformations** - Mirror, rotate, and invert images

## Installation

### From PyPI

```bash
pip install piltext
```

### From Source

```bash
git clone https://github.com/holgern/piltext.git
cd piltext
python3 setup.py install
```

## Quick Start

### Simple Text Rendering

```python
from piltext import FontManager, ImageDrawer

# Initialize with font manager
fm = FontManager(default_font_size=20)
image = ImageDrawer(400, 200, font_manager=fm)

# Draw text
image.draw_text("Hello World", (50, 50), font_size=32, fill="black")
image.finalize()
image.show()
```

### Using TOML Configuration

Create `config.toml`:

```toml
[fonts]
default_size = 24

[image]
width = 400
height = 200

[grid]
rows = 2
columns = 2
margin_x = 5
margin_y = 5

[[grid.texts]]
start = [0, 0]
text = "Hello"
anchor = "mm"

[[grid.texts]]
start = [0, 1]
text = "World"
anchor = "mm"
```

Render from command line:

```bash
piltext render config.toml --output output.png
```

Or from Python:

```python
from piltext import ConfigLoader

loader = ConfigLoader("config.toml")
image = loader.render(output_path="output.png")
```

## Python API

### Font Management

```python
from piltext import FontManager

# Initialize with default font size
fm = FontManager(default_font_size=20)

# Download Google Fonts
font = fm.download_google_font("ofl", "roboto", "Roboto[wdth,wght].ttf")
fm.default_font_name = font

# List available fonts
print(fm.list_available_fonts())

# Get font variations (for variable fonts)
print(fm.get_variation_names())
```

### Drawing Text

```python
from piltext import FontManager, ImageDrawer

fm = FontManager(default_font_size=20)
image = ImageDrawer(480, 280, font_manager=fm)

# Basic text drawing
w, h, font_size = image.draw_text("Hello", (10, 10), font_size=24)

# Auto-fit text to bounding box (no font_size specified)
w, h, font_size = image.draw_text(
    "Auto-Fit Text",
    start=(10, 50),
    end=(200, 100),
    anchor="mm"  # Center the text
)

# Fixed font size with anchor
w, h, font_size = image.draw_text(
    "Fixed Size",
    (400, 250),
    font_size=20,
    anchor="rb"  # Right-bottom
)

image.finalize()
image.show()
```

### Anchor Positioning

Anchors control text alignment using a two-character code: `[horizontal][vertical]`

**Horizontal:** `l` (left), `m` (middle), `r` (right) **Vertical:** `t` (top), `m`
(middle), `b` (bottom), `s` (baseline)

Common anchors:

- `lt` - Left-top (default)
- `mm` - Centered
- `rb` - Right-bottom
- `mt` - Middle-top
- `lb` - Left-bottom

**Auto-fit behavior:**

- When `font_size` is **not specified**: Text scales to fit the bounding box, then
  positions using the anchor
- When `font_size` **is specified**: Text uses fixed size and positions using the anchor
  (no scaling)

### Grid Layouts

```python
from piltext import FontManager, ImageDrawer, TextGrid

fm = FontManager(default_font_size=20)
image = ImageDrawer(480, 280, font_manager=fm)

# Create grid
grid = TextGrid(4, 3, image, margin_x=5, margin_y=5)

# Merge cells: ((start_row, start_col), (end_row, end_col))
merge_list = [
    ((0, 0), (0, 2)),  # Merge row 0, columns 0-2
    ((1, 1), (2, 2)),  # Merge rows 1-2, columns 1-2
]
grid.merge_bulk(merge_list)

# Add text to cells
grid.set_text((0, 0), "Header", anchor="mm", font_size=28)
grid.set_text((1, 0), "Cell 1", anchor="lt")
grid.set_text((1, 1), "Large Cell", anchor="mm")

image.finalize()
image.show()
```

### Bulk Text Setting

```python
text_list = [
    {"start": (0, 0), "text": "Header", "font_size": 28, "anchor": "mm"},
    {"start": (1, 0), "text": "Cell 1", "anchor": "lt"},
    {"start": (1, 1), "text": "Cell 2", "anchor": "mm", "fill": 128},
]
grid.set_text_list(text_list)
```

### Visualizations

#### Dial Gauge

```python
from piltext import ImageDial

dial = ImageDial(
    percentage=0.75,
    size=300,
    fg_color="#4CAF50",
    track_color="#e0e0e0",
    show_value=True
)
dial.show()
```

#### Waffle Chart

```python
from piltext import ImageSquares

squares = ImageSquares(
    percentage=0.65,
    max_squares=100,
    size=300,
    fg_color="#2196F3",
    empty_color="#e0e0e0"
)
squares.show()
```

## TOML Configuration Reference

### Complete Example

```toml
[fonts]
default_size = 20
default_name = "Roboto-Bold"
directories = ["/path/to/fonts"]

[[fonts.download]]
part1 = "ofl"
part2 = "roboto"
font_name = "Roboto[wdth,wght].ttf"

[image]
width = 480
height = 280
mode = "RGB"
background = "white"
inverted = false
mirror = false
orientation = 0

[grid]
rows = 4
columns = 3
margin_x = 5
margin_y = 5

merge = [
  [[0, 0], [0, 2]],  # Header row
  [[1, 1], [2, 2]]   # Large cell
]

[[grid.texts]]
start = [0, 0]
text = "Header"
anchor = "mm"
font_size = 28
fill = 0

[[grid.texts]]
start = [1, 0]
text = "Data"
anchor = "lt"
font_variation = "Bold"

# Embed dial in grid cell
[[grid.texts]]
start = [1, 1]
anchor = "mm"

[grid.texts.dial]
percentage = 0.75
fg_color = "#4CAF50"
show_value = true

# Embed waffle chart in grid cell
[[grid.texts]]
start = [3, 2]
anchor = "mm"

[grid.texts.squares]
percentage = 0.60
rows = 5
columns = 5
fg_color = "#2196F3"
```

### Configuration Sections

#### Fonts

```toml
[fonts]
default_size = 20              # Default font size in pixels
default_name = "Roboto-Bold"   # Default font name
directories = ["/path/to/fonts"]  # Custom font directories (optional)

# Download fonts before rendering (optional)
# From Google Fonts
[[fonts.download]]
part1 = "ofl"                  # Google Fonts: license type
part2 = "roboto"               # Google Fonts: font family
font_name = "Roboto[wdth,wght].ttf"

# Or from direct URL
[[fonts.download]]
url = "https://example.com/font.ttf"
```

#### Image

```toml
[image]
width = 480                    # Image width in pixels
height = 280                   # Image height in pixels
mode = "RGB"                   # PIL mode: RGB, RGBA, L, 1
background = "white"           # Background color
inverted = false               # Invert colors
mirror = false                 # Mirror horizontally
orientation = 0                # Rotation angle (0, 90, 180, 270)
```

#### Grid

```toml
[grid]
rows = 4                       # Number of rows
columns = 3                    # Number of columns
margin_x = 5                   # Horizontal margin in pixels
margin_y = 5                   # Vertical margin in pixels

# Merge cells (optional)
merge = [
  [[0, 0], [2, 0]],            # Merge rows 0-2, column 0
]

# Text content
[[grid.texts]]
start = [0, 0]                 # Cell position (or merged cell index)
text = "Content"               # Text to display
font_name = "Roboto"           # Font name (optional)
font_size = 24                 # Font size (optional, triggers auto-fit if omitted)
font_variation = "Bold"        # Font variation (optional)
fill = 0                       # Text color (optional, default: 0 for black)
anchor = "mm"                  # Anchor position (optional, default: "lt")
```

#### Standalone Dial

```toml
[dial]
percentage = 0.75              # Value from 0.0 to 1.0
size = 300                     # Image size in pixels
radius = 120                   # Dial radius (optional, auto-calculated)
fg_color = "#4CAF50"           # Arc color for filled portion
track_color = "#e0e0e0"        # Background arc color
bg_color = "white"             # Background color
thickness = 20                 # Arc thickness in pixels
font_name = "Roboto-Bold"      # Font for labels (optional)
font_size = 24                 # Font size (optional)
show_needle = true             # Show needle pointer
show_ticks = true              # Show tick marks
show_value = true              # Show percentage in center
start_angle = -135             # Start angle in degrees
end_angle = 135                # End angle in degrees
```

#### Standalone Waffle Chart

```toml
[squares]
percentage = 0.65              # Value from 0.0 to 1.0
max_squares = 100              # Total number of squares
size = 300                     # Image size in pixels
rows = 10                      # Number of rows (optional)
columns = 10                   # Number of columns (optional)
fg_color = "#4CAF50"           # Fill color
empty_color = "#e0e0e0"        # Empty square color
bg_color = "white"             # Background color
gap = 2                        # Gap between squares in pixels
border_width = 1               # Border width
border_color = "#cccccc"       # Border color
show_partial = true            # Partially fill last square
```

**Priority:** `dial` > `squares` > `grid` > `image`

## CLI Commands

### Render Images

```bash
# Render from TOML config
piltext render config.toml -o output.png

# Render with specific output
piltext render examples/example_dial.toml --output my_dial.png
```

### Font Management

```bash
# List available fonts
piltext font list

# Download Google Font
piltext font download ofl roboto Roboto-Regular.ttf

# List font variations
piltext font variations "Roboto[wdth,wght]"
```

## Examples

See the `examples/` directory for complete examples:

- `example_simple.toml` - Basic text grid
- `example_grid_with_visualizations.toml` - Grid with embedded charts
- `example_dial.toml` - Standalone dial gauge
- `example_squares.toml` - Standalone waffle chart
- `example_config.toml` - Complete configuration example

## Development

### Running Tests

```bash
pytest
pytest --cov=piltext --cov-report=term
```

### Type Checking

```bash
mypy piltext
```

### Linting

```bash
ruff check --fix --config=.ruff.toml
```

### Pre-commit Hooks

Install pre-commit:

```bash
pip install pre-commit
# or
brew install pre-commit
```

Install hooks:

```bash
pre-commit install
```

Run hooks:

```bash
pre-commit run --all-files
```

Update hooks:

```bash
pre-commit autoupdate
pre-commit run --show-diff-on-failure --color=always --all-files
```

## Documentation

Full API documentation is available at [Read the Docs](https://piltext.readthedocs.io/).

Build documentation locally:

```bash
cd docs
python make.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass and linting/type checking succeeds
5. Submit a pull request

## Changelog

### Recent Improvements

- ✅ Fixed auto-fit behavior with custom anchors (text with `rb`, `mm`, etc. now renders
  correctly)
- ✅ Added comprehensive test coverage (48%+ overall, 100% for core modules)
- ✅ Full mypy type checking support
- ✅ Improved documentation with detailed examples
