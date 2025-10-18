JSON Data Input Guide
=====================

Overview
--------

The ``piltext render`` command supports data-driven image generation by reading JSON from stdin. This allows you to create templates in TOML and populate them dynamically with data from JSON.

Usage
-----

.. code-block:: bash

   piltext render template.toml --json-input --output image.png < data.json
   echo '{"key": "value"}' | piltext render template.toml --json-input -o image.png
   echo '["value1", "value2", "value3"]' | piltext render template.toml --json-input -o image.png

Three Modes of Operation
-------------------------

1. Simple Array (Easiest)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Pass a JSON array and values are mapped to text items in order:

**Example:**

.. code-block:: bash

   # For a template with 4 text items
   echo '["Line 1", "Line 2", "Line 3", "Line 4"]' | \
     piltext render examples/example_simple.toml --json-input -o output.png

   # For metrics with dials/squares (values are percentages 0.0-1.0)
   echo '[0.65, 0.82, 0.44]' | \
     piltext render template_metrics.toml --json-input -o metrics.png

   # Works with any values (numbers, strings, etc.)
   echo '["CPU", "72%", 42, "Active"]' | \
     piltext render template.toml --json-input -o output.png

**How it works:**

- First array item → first ``[[grid.texts]]`` item
- Second array item → second ``[[grid.texts]]`` item
- And so on...
- For text items: values are converted to strings
- For dials/squares: values are treated as percentages
- Extra array items are ignored
- Missing items keep their template defaults

2. Data Binding with Named Keys (Best for Complex Templates)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``data_key`` in your TOML template to bind JSON values to specific fields:

**Template (template.toml):**

.. code-block:: toml

   [fonts]
   default_size = 24

   [image]
   width = 600
   height = 400

   [grid]
   rows = 2
   columns = 2

   [[grid.texts]]
   start = [0, 0]
   text = "Temperature"
   anchor = "mm"

   [[grid.texts]]
   start = [0, 1]
   data_key = "temperature"  # Binds to JSON field
   anchor = "mm"
   font_size = 32
   fill_key = "temp_color"   # Color from JSON

   [[grid.texts]]
   start = [1, 0]
   text = "Humidity"
   anchor = "mm"

   [[grid.texts]]
   start = [1, 1]
   data_key = "humidity"
   anchor = "mm"
   font_size = 32

**Data (data.json):**

.. code-block:: json

   {"temperature": "72°F", "humidity": "45%", "temp_color": "#FF5722"}

**Command:**

.. code-block:: bash

   cat data.json | piltext render template.toml --json-input -o output.png

3. Configuration Override
~~~~~~~~~~~~~~~~~~~~~~~~~~

Override any configuration value directly:

.. code-block:: bash

   echo '{"image": {"width": 800}}' | piltext render config.toml --json-input -o output.png

Quick Comparison
----------------

+-------------------+------------------------------------------+------------------------------------+
| Mode              | When to Use                              | Example                            |
+===================+==========================================+====================================+
| **Array**         | Simple templates, quick data injection   | ``["A", "B", "C"]``                |
+-------------------+------------------------------------------+------------------------------------+
| **Named Keys**    | Complex templates, specific targeting    | ``{"temp": "72°F", "city": "NYC"}``|
+-------------------+------------------------------------------+------------------------------------+
| **Config Override** | Dynamic configuration changes          | ``{"image": {"width": 1000}}``     |
+-------------------+------------------------------------------+------------------------------------+

Data Binding Keys
-----------------

For Text Fields
~~~~~~~~~~~~~~~

- ``data_key`` - Binds the text content from JSON
- ``fill_key`` - Binds the text color from JSON
- ``font_size_key`` - Binds the font size from JSON
- ``font_name_key`` - Binds the font name from JSON

For Visualizations (Dials & Squares)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a text item has a ``dial`` or ``squares`` section, ``data_key`` binds to the percentage:

**Template:**

.. code-block:: toml

   [[grid.texts]]
   start = [0, 0]
   data_key = "cpu_usage"

   [grid.texts.dial]
   size = 220
   fg_color = "#4CAF50"
   show_value = true

**Data:**

.. code-block:: json

   {"cpu_usage": 0.75}

This sets the dial to 75% (0.75 as a percentage value).

Complete Examples
-----------------

Example 1: System Metrics Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Template (metrics.toml):**

.. code-block:: toml

   [fonts]
   default_size = 24

   [image]
   width = 900
   height = 300

   [grid]
   rows = 1
   columns = 3
   margin_x = 20
   margin_y = 20

   # CPU Dial
   [[grid.texts]]
   start = [0, 0]
   data_key = "cpu"

   [grid.texts.dial]
   size = 220
   fg_color = "#4CAF50"
   show_value = true

   # Memory Dial
   [[grid.texts]]
   start = [0, 1]
   data_key = "memory"

   [grid.texts.dial]
   size = 220
   fg_color = "#FF9800"
   show_value = true

   # Disk Usage Squares
   [[grid.texts]]
   start = [0, 2]
   data_key = "disk"

   [grid.texts.squares]
   rows = 10
   columns = 10
   fg_color = "#2196F3"

**Generate images with different data:**

.. code-block:: bash

   # Current metrics
   echo '{"cpu": 0.45, "memory": 0.72, "disk": 0.33}' | \
     piltext render metrics.toml --json-input -o metrics_now.png

   # Peak metrics
   echo '{"cpu": 0.95, "memory": 0.88, "disk": 0.91}' | \
     piltext render metrics.toml --json-input -o metrics_peak.png

Example 2: Weather Display
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Template (weather.toml):**

.. code-block:: toml

   [fonts]
   default_size = 32

   [image]
   width = 800
   height = 300

   [grid]
   rows = 2
   columns = 3

   [[grid.texts]]
   start = [0, 0]
   text = "City"
   [[grid.texts]]
   start = [0, 1]
   data_key = "city"

   [[grid.texts]]
   start = [0, 2]
   text = "Temp"
   [[grid.texts]]
   start = [0, 3]
   data_key = "temperature"
   fill_key = "temp_color"

   [[grid.texts]]
   start = [1, 0]
   text = "Conditions"
   [[grid.texts]]
   start = [1, 1]
   data_key = "conditions"

   [[grid.texts]]
   start = [1, 2]
   text = "Humidity"
   [[grid.texts]]
   start = [1, 3]
   data_key = "humidity"

**Stream weather data:**

.. code-block:: bash

   # From API or data pipeline
   curl https://api.weather.example/data | \
     jq '{"city": .location, "temperature": .temp, "conditions": .weather, "humidity": .humidity_pct, "temp_color": .color}' | \
     piltext render weather.toml --json-input -o weather.png

Example 3: Multiple JSON Lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Process multiple lines sequentially (each line updates the config):

.. code-block:: bash

   printf '{"temperature": "70°F"}\n{"humidity": "50%%"}\n' | \
     piltext render template.toml --json-input -o output.png

Example 4: CI/CD Build Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Template (build_status.toml):**

.. code-block:: toml

   [image]
   width = 600
   height = 200

   [grid]
   rows = 2
   columns = 2

   [[grid.texts]]
   start = [0, 0]
   text = "Build"
   [[grid.texts]]
   start = [0, 1]
   data_key = "build_number"

   [[grid.texts]]
   start = [1, 0]
   text = "Status"
   [[grid.texts]]
   start = [1, 1]
   data_key = "status"
   fill_key = "status_color"
   font_size_key = "status_size"

**In your CI pipeline:**

.. code-block:: bash

   # Success
   echo '{"build_number": "#123", "status": "PASSED", "status_color": "#4CAF50", "status_size": 48}' | \
     piltext render build_status.toml --json-input -o badge.png

   # Failure
   echo '{"build_number": "#124", "status": "FAILED", "status_color": "#F44336", "status_size": 48}' | \
     piltext render build_status.toml --json-input -o badge.png

Use Cases
---------

1. **Monitoring Dashboards** - Generate status images from metrics
2. **CI/CD Pipelines** - Create build badges with dynamic data
3. **Report Generation** - Populate report templates with database queries
4. **IoT Displays** - Show sensor data on e-ink displays
5. **Data Visualization** - Convert JSON API responses to images
6. **Automated Alerts** - Generate status images for notifications

Tips
----

- Empty JSON lines are ignored
- Invalid JSON lines generate errors but don't stop processing
- Multiple lines are processed sequentially
- Later values override earlier ones
- Percentage values for dials/squares should be between 0.0 and 1.0
- Use ``jq`` to transform complex JSON to the format you need
- Both compact (single-line) and pretty-printed (multi-line) JSON are supported

Error Handling
--------------

If JSON parsing fails, an error message is displayed but processing continues:

.. code-block:: bash

   $ echo '{"invalid": json}' | piltext render template.toml --json-input
   Error parsing JSON: Expecting value: line 1 column 13 (char 12)
