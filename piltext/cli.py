from typing import Annotated, Optional

import typer

from .ascii_art import display_as_ascii
from .config_loader import ConfigLoader
from .font_manager import FontManager

try:
    from rich.console import Console
    from rich_pixels import Pixels

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

app = typer.Typer(
    name="piltext",
    help="CLI tool for managing fonts and creating images from text",
    add_completion=False,
)

font_app = typer.Typer(help="Font management commands")
app.add_typer(font_app, name="font")


@font_app.command("list")
def list_fonts(
    fullpath: Annotated[
        bool, typer.Option("--fullpath", "-f", help="Show full paths to font files")
    ] = False,
    fontdir: Annotated[
        Optional[str],
        typer.Option("--fontdir", "-d", help="Custom font directory to search"),
    ] = None,
):
    fm = FontManager(fontdirs=fontdir) if fontdir else FontManager()
    fonts = fm.list_available_fonts(fullpath=fullpath)

    if not fonts:
        typer.echo("No fonts found", err=True)
        raise typer.Exit(1)

    for font in sorted(fonts):
        typer.echo(font)


@font_app.command("dirs")
def list_directories(
    fontdir: Annotated[
        Optional[str],
        typer.Option("--fontdir", "-d", help="Custom font directory to add"),
    ] = None,
):
    fm = FontManager(fontdirs=fontdir) if fontdir else FontManager()
    dirs = fm.list_font_directories()

    for directory in dirs:
        typer.echo(directory)


@font_app.command("download")
def download_font(
    part1: Annotated[str, typer.Argument(help="First part of font path (e.g., 'ofl')")],
    part2: Annotated[
        str, typer.Argument(help="Second part of font path (e.g., 'roboto')")
    ],
    font_name: Annotated[
        str, typer.Argument(help="Font file name (e.g., 'Roboto-Regular.ttf')")
    ],
    fontdir: Annotated[
        Optional[str],
        typer.Option(
            "--fontdir", "-d", help="Custom font directory to download font to"
        ),
    ] = None,
):
    fm = FontManager(fontdirs=fontdir) if fontdir else FontManager()

    try:
        font_path = fm.download_google_font(part1, part2, font_name)
        typer.echo(f"Successfully downloaded font to: {font_path}")
    except Exception as e:
        typer.echo(f"Error downloading font: {e}", err=True)
        raise typer.Exit(1) from None


@font_app.command("download-url")
def download_font_url(
    url: Annotated[str, typer.Argument(help="URL of the font file to download")],
    fontdir: Annotated[
        Optional[str],
        typer.Option(
            "--fontdir", "-d", help="Custom font directory to download font to"
        ),
    ] = None,
):
    fm = FontManager(fontdirs=fontdir) if fontdir else FontManager()

    try:
        font_path = fm.download_font(url)
        typer.echo(f"Successfully downloaded font to: {font_path}")
    except Exception as e:
        typer.echo(f"Error downloading font: {e}", err=True)
        raise typer.Exit(1) from None


@font_app.command("variations")
def list_variations(
    font_name: Annotated[str, typer.Argument(help="Font name to check variations")],
    fontdir: Annotated[
        Optional[str],
        typer.Option("--fontdir", "-d", help="Custom font directory to search"),
    ] = None,
):
    fm = FontManager(fontdirs=fontdir) if fontdir else FontManager()

    try:
        variations = fm.get_variation_names(font_name=font_name)
        if variations:
            for variation in variations:
                typer.echo(variation)
        else:
            typer.echo(f"No variations found for font: {font_name}")
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error getting variations: {e}", err=True)
        raise typer.Exit(1) from None


@font_app.command("delete-all")
def delete_all_fonts(
    fontdir: Annotated[
        Optional[str],
        typer.Option("--fontdir", "-d", help="Custom font directory to clear"),
    ] = None,
    confirm: Annotated[
        bool,
        typer.Option(
            "--yes", "-y", help="Skip confirmation prompt and delete all fonts"
        ),
    ] = False,
):
    fm = FontManager(fontdirs=fontdir) if fontdir else FontManager()

    if not confirm:
        dirs = ", ".join(fm.list_font_directories())
        proceed = typer.confirm(
            f"Are you sure you want to delete all fonts from: {dirs}?"
        )
        if not proceed:
            typer.echo("Aborted")
            raise typer.Exit(0)

    deleted_fonts = fm.delete_all_fonts()

    if deleted_fonts:
        typer.echo(f"Deleted {len(deleted_fonts)} fonts:")
        for font in deleted_fonts:
            typer.echo(f"  - {font}")
    else:
        typer.echo("No fonts to delete")


@app.command("render")
def render_from_config(
    config: Annotated[str, typer.Argument(help="Path to YAML configuration file")],
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Output image file path (PNG)"),
    ] = None,
    display: Annotated[
        bool,
        typer.Option(
            "--display", "-d", help="Display image in terminal using rich-pixels"
        ),
    ] = False,
    ascii_art: Annotated[
        bool,
        typer.Option("--ascii", "-a", help="Display image as ASCII art"),
    ] = False,
    simple_ascii: Annotated[
        bool,
        typer.Option(
            "--simple", "-s", help="Use simple ASCII characters (space, dot, hash)"
        ),
    ] = False,
    display_width: Annotated[
        Optional[int],
        typer.Option(
            "--display-width", help="Width for terminal display (in characters)"
        ),
    ] = None,
    display_height: Annotated[
        Optional[int],
        typer.Option(
            "--display-height", help="Height for terminal display (in characters)"
        ),
    ] = None,
):
    import os
    import tempfile

    try:
        loader = ConfigLoader(config)

        if display and not RICH_AVAILABLE:
            typer.echo(
                "Error: rich-pixels not installed. "
                "Install with: pip install rich-pixels",
                err=True,
            )
            raise typer.Exit(1)

        resize = None
        if display_width is not None or display_height is not None:
            resize = (display_width, display_height)

        if (ascii_art or simple_ascii) and not output:
            img = loader.render()
            ascii_output = display_as_ascii(
                img,
                columns=display_width or 80,
                char=" .#" if simple_ascii else None,
                monochrome=simple_ascii,
            )
            typer.echo(ascii_output)
        elif (ascii_art or simple_ascii) and output:
            img = loader.render(output_path=output)
            typer.echo(f"Image saved to: {output}")
            ascii_output = display_as_ascii(
                img,
                columns=display_width or 80,
                char=" .#" if simple_ascii else None,
                monochrome=simple_ascii,
            )
            typer.echo(ascii_output)
        elif display and not output:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_path = tmp.name
                loader.render(output_path=temp_path)

                if RICH_AVAILABLE:
                    console = Console()  # type: ignore
                    pixels = Pixels.from_image_path(temp_path, resize=resize)  # type: ignore
                    console.print(pixels)

                os.unlink(temp_path)
        elif display and output:
            loader.render(output_path=output)
            typer.echo(f"Image saved to: {output}")

            if RICH_AVAILABLE:
                console = Console()  # type: ignore
                pixels = Pixels.from_image_path(output, resize=resize)  # type: ignore
                console.print(pixels)
        elif output:
            loader.render(output_path=output)
            typer.echo(f"Image saved to: {output}")
        else:
            typer.echo(
                "Please specify --output to save or --display to show in terminal",
                err=True,
            )
            raise typer.Exit(1)

    except FileNotFoundError as e:
        typer.echo(f"Error: Config file not found - {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"Error rendering image: {e}", err=True)
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
