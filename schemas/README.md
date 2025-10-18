# Piltext JSON Schema

This directory contains the JSON Schema for piltext TOML configuration files.

## Schema File

- `piltext.json` - JSON Schema for piltext TOML configurations

## Usage

The schema provides:

- **Validation** - Ensures TOML files follow the correct structure
- **Autocomplete** - Provides intelligent suggestions in editors (VS Code with Even
  Better TOML extension)
- **Documentation** - Shows inline help for configuration options
- **Type checking** - Validates data types and required fields

## Editor Support

### VS Code

1. Install the
   [Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)
   extension
2. The schema is automatically associated with piltext TOML files via `.taplo.toml`
3. You'll get autocompletion, validation, and documentation on hover

### Command Line

Use `taplo` CLI for validation:

```bash
# Check a single file
taplo check examples/example_config.toml

# Check all example files
taplo check examples/*.toml

# Format TOML files
taplo format examples/*.toml
```

## Schema Structure

The schema supports four main configuration modes:

### 1. Grid Mode

Create text-based grid layouts with merged cells:

```toml
[fonts]
default_size = 16

[image]
width = 800
height = 600

[grid]
rows = 4
columns = 4
merge = [[[0, 0], [0, 3]]]  # Merge first row

[[grid.texts]]
start = 0
text = "Header"
```

### 2. Dial Mode

Create circular gauge visualizations:

```toml
[fonts]
default_size = 20

[dial]
percentage = 0.75
size = 300
fg_color = "#4CAF50"
show_needle = true
```

### 3. Squares Mode

Create waffle chart visualizations:

```toml
[fonts]
default_size = 12

[squares]
percentage = 0.65
max_squares = 100
rows = 10
columns = 10
fg_color = "#4CAF50"
```

### 4. Embedded Visualizations

Embed dials and squares in grid cells:

```toml
[grid]
rows = 2
columns = 2

[[grid.texts]]
start = [0, 0]

[grid.texts.dial]
percentage = 0.75
size = 200
```

## Configuration Sections

### `[fonts]`

Font management and settings:

- `default_size` - Default font size in pixels
- `default_name` - Default font name or path
- `directories` - Custom font directories
- `download` - Fonts to download from Google Fonts or URLs

### `[image]`

Image properties:

- `width`, `height` - Image dimensions
- `mode` - Color mode (RGB, RGBA, L, 1)
- `background` - Background color
- `inverted`, `mirror`, `orientation` - Transformations

### `[grid]`

Grid layout configuration:

- `rows`, `columns` - Grid dimensions
- `margin_x`, `margin_y` - Cell spacing
- `merge` - Cell merge definitions
- `texts` - Text elements to render

### `[dial]`

Circular gauge configuration:

- `percentage` - Value to display (0.0-1.0)
- `size`, `radius`, `thickness` - Dimensions
- `fg_color`, `track_color`, `bg_color` - Colors
- `start_angle`, `end_angle` - Arc range
- `show_needle`, `show_ticks`, `show_value` - Display options

### `[squares]`

Waffle chart configuration:

- `percentage` - Value to display (0.0-1.0)
- `max_squares` - Total number of squares
- `rows`, `columns` - Grid dimensions
- `fg_color`, `empty_color`, `bg_color` - Colors
- `gap`, `border_width`, `border_color` - Styling
- `show_partial` - Show partial square filling

## Extension Fields

The schema uses Taplo's `x-taplo` extension for enhanced editor support:

- `docs.main` - Main documentation for each field
- `docs.enumValues` - Documentation for enum values
- `links.key` - URL links for configuration keys
- `initKeys` - Fields to auto-create during completion
- `hidden` - Hide fields from autocompletion

## Schema Updates

When adding new configuration options:

1. Update `piltext.json` with new fields
2. Add appropriate `x-taplo` documentation
3. Test with `taplo check examples/*.toml`
4. Update this README if adding new sections

## Validation

The schema validates:

- Required fields for each mode
- Data types (string, integer, number, boolean, array, object)
- Value ranges (e.g., percentage between 0.0 and 1.0)
- Enum values (e.g., image mode must be RGB, RGBA, L, or 1)
- Array structures (e.g., merge definitions, cell coordinates)

## Examples

See the `examples/` directory for complete, validated configuration files:

- `example_config.toml` - Basic grid layout
- `example_advanced_grid.toml` - Complex grid with styling
- `example_dial.toml` - Simple circular gauge
- `example_advanced_dial.toml` - Custom styled gauge
- `example_squares.toml` - Basic waffle chart
- `example_advanced_squares.toml` - Styled waffle chart
- `example_grid_with_visualizations.toml` - Embedded visualizations

## Contributing

When contributing schema changes:

1. Follow JSON Schema Draft 7 specification
2. Add descriptive `description` fields
3. Include `x-taplo` documentation for user-facing fields
4. Test validation with all example files
5. Update this README with new features
