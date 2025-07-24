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

Font Management
--------------

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

Text Grids
----------

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
