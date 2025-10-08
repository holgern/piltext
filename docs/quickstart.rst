Quickstart
==========

Installation
-----------

You can install PILText using pip:

.. code-block:: bash

   pip install piltext

Basic Usage
----------

PILText provides tools to create images with text using Pillow (PIL).

.. code-block:: python

   import piltext
   from piltext.image_handler import ImageHandler
   from piltext.text_box import TextBox

   # Create a new image with a text box
   handler = ImageHandler(width=400, height=200, background_color="white")
   text_box = TextBox(
       text="Hello World!",
       x=200,
       y=100,
       font_size=36,
       align="center",
       color="black"
   )

   # Draw the text on the image
   handler.draw_text_box(text_box)

   # Save the image
   handler.save("hello_world.png")

YAML Configuration
-----------------

PILText supports YAML configuration files for easy image generation:

.. code-block:: yaml

   fonts:
     default_size: 24

   image:
     width: 400
     height: 200

   grid:
     rows: 2
     columns: 2
     margin_x: 5
     margin_y: 5

     texts:
       - start: [0, 0]
         text: "Hello"
         anchor: "mm"

       - start: [0, 1]
         text: "World"
         anchor: "mm"

Render from CLI:

.. code-block:: bash

   piltext render config.yaml --output output.png

Or from Python:

.. code-block:: python

   from piltext import ConfigLoader

   loader = ConfigLoader("config.yaml")
   image = loader.render(output_path="output.png")

Configuration Options
~~~~~~~~~~~~~~~~~~~~

**Fonts Section:**

.. code-block:: yaml

   fonts:
     default_size: 20              # Default font size in pixels
     default_name: "Roboto-Bold"   # Default font name

     # Optional: Custom font directories
     directories:
       - /path/to/fonts

     # Optional: Download fonts before rendering
     download:
       # From Google Fonts
       - part1: "ofl"
         part2: "roboto"
         font_name: "Roboto[wdth,wght].ttf"

       # From URL
       - url: "https://example.com/font.ttf"

**Image Section:**

.. code-block:: yaml

   image:
     width: 480                    # Image width in pixels
     height: 280                   # Image height in pixels
     inverted: false               # Invert colors
     mirror: false                 # Mirror horizontally
     orientation: 0                # Rotation angle

**Grid Section:**

.. code-block:: yaml

   grid:
     rows: 4                       # Number of rows
     columns: 7                    # Number of columns
     margin_x: 2                   # Horizontal margin in pixels
     margin_y: 2                   # Vertical margin in pixels

     # Merge cells: [[start_row, start_col], [end_row, end_col]]
     merge:
       - [[0, 0], [0, 3]]          # Merge row 0, columns 0-3
       - [[1, 0], [2, 1]]          # Merge rows 1-2, columns 0-1

     # Text content
     texts:
       - start: 0                  # Merged cell index
         text: "Header"
         font_variation: "Bold"
         fill: 255
         anchor: "mm"              # Anchor: lt/mm/rs etc.

       - start: [1, 2]             # Or use [row, col]
         text: "Cell Text"
         font_name: "CustomFont"
         fill: 128

**Anchor Options:**

- ``lt`` - left-top
- ``mm`` - middle-middle
- ``rs`` - right-side
- And more PIL text anchor options

CLI Commands
-----------

Rendering
~~~~~~~~~

Render from config file:

.. code-block:: bash

   # Save to file
   piltext render config.yaml -o output.png

   # Display in terminal (requires rich-pixels)
   piltext render config.yaml -d

   # Display as ASCII art
   piltext render config.yaml -a

   # Display as simple ASCII art (uses only space, dot, hash)
   piltext render config.yaml -a -s

   # Control display width
   piltext render config.yaml -a --display-width 100

   # Save and display
   piltext render config.yaml -o output.png -d

Font Management
~~~~~~~~~~~~~~

List available fonts:

.. code-block:: bash

   # List font names
   piltext font list

   # List with full paths
   piltext font list --fullpath

List font directories:

.. code-block:: bash

   piltext font dirs

Download Google Fonts:

.. code-block:: bash

   piltext font download ofl roboto Roboto-Regular.ttf

Download from URL:

.. code-block:: bash

   piltext font download-url https://example.com/font.ttf

List font variations:

.. code-block:: bash

   piltext font variations Roboto[wdth,wght]

Delete all fonts:

.. code-block:: bash

   # With confirmation
   piltext font delete-all

   # Skip confirmation
   piltext font delete-all -y

Font Management (Python)
------------------------

PILText includes a font manager to handle font loading and selection:

.. code-block:: python

   from piltext.font_manager import FontManager

   # Initialize font manager
   font_manager = FontManager()

   # Add a font path
   font_manager.add_font_path("path/to/custom_font.ttf")

   # Use Google Fonts
   font_manager.use_google_font("Roboto")

   # Get a font instance
   font = font_manager.get_font(font_name="Roboto", size=24)

Text Grids (Python)
-------------------

PILText supports grid-based text layouts:

.. code-block:: python

   from piltext.text_grid import TextGrid

   # Create a text grid with 2 rows and 3 columns
   grid = TextGrid(rows=2, cols=3, width=600, height=400)

   # Add text to specific cells
   grid.add_text("Cell 1", row=0, col=0)
   grid.add_text("Cell 2", row=0, col=1)
   grid.add_text("Cell 3", row=0, col=2)
   grid.add_text("Cell 4", row=1, col=0)
   grid.add_text("Cell 5", row=1, col=1)
   grid.add_text("Cell 6", row=1, col=2)

   # Render the grid
   img = grid.render()
   img.save("text_grid.png")
