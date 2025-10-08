from typing import Annotated, Optional

import typer

from .ascii_art import display_as_ascii, display_readable_text, generate_ascii_art_text
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


def _extract_text_and_colors(loader: ConfigLoader):
    grid_config = loader.config.get("grid", {})
    text_list = grid_config.get("texts", [])
    if not text_list:
        typer.echo("No text content found in configuration", err=True)
        raise typer.Exit(1)
    texts = [item.get("text", "") for item in text_list]
    colors = [item.get("fill") for item in text_list]
    return texts, colors


def _handle_text_only(
    loader: ConfigLoader, display_width: Optional[int], line_spacing: int
):
    texts, colors = _extract_text_and_colors(loader)
    readable_output = display_readable_text(
        texts,
        width=display_width or 80,
        line_spacing=line_spacing,
        center=True,
        colors=colors,
    )
    typer.echo(readable_output, color=True)


def _handle_figlet(
    loader: ConfigLoader,
    figlet_font: str,
    display_width: Optional[int],
    line_spacing: int,
):
    texts, colors = _extract_text_and_colors(loader)
    try:
        figlet_output = generate_ascii_art_text(
            texts,
            font=figlet_font,
            width=display_width,
            line_spacing=line_spacing,
            colors=colors,
        )
        typer.echo(figlet_output, color=True)
    except ImportError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from None


def _handle_ascii_art(
    loader: ConfigLoader,
    output: Optional[str],
    display_width: Optional[int],
    simple_ascii: bool,
):
    if output:
        img = loader.render(output_path=output)
        typer.echo(f"Image saved to: {output}")
    else:
        img = loader.render()

    ascii_output = display_as_ascii(
        img,
        columns=display_width or 80,
        char=" .#" if simple_ascii else None,
        monochrome=simple_ascii,
    )
    typer.echo(ascii_output, color=True)


def _handle_display(
    loader: ConfigLoader,
    output: Optional[str],
    resize: Optional[tuple[Optional[int], Optional[int]]],
):
    import os
    import tempfile

    if output:
        loader.render(output_path=output)
        typer.echo(f"Image saved to: {output}")
        image_path = output
        temp_path = None
    else:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name
        loader.render(output_path=temp_path)
        image_path = temp_path

    if RICH_AVAILABLE:
        console = Console()  # type: ignore
        pixels = Pixels.from_image_path(image_path, resize=resize)  # type: ignore
        console.print(pixels)

    if temp_path:
        os.unlink(temp_path)


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
    text_only: Annotated[
        bool,
        typer.Option(
            "--text-only", "-t", help="Display only the text content in readable format"
        ),
    ] = False,
    figlet: Annotated[
        bool,
        typer.Option(
            "--figlet", "-f", help="Display text as large ASCII art (requires pyfiglet)"
        ),
    ] = False,
    figlet_font: Annotated[
        str,
        typer.Option(
            "--figlet-font", help="FIGlet font name (e.g., standard, slant, banner)"
        ),
    ] = "standard",
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
    line_spacing: Annotated[
        int,
        typer.Option(
            "--line-spacing",
            help="Number of blank lines between text items (for --text-only)",
        ),
    ] = 1,
):
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

        if text_only:
            _handle_text_only(loader, display_width, line_spacing)
        elif figlet:
            _handle_figlet(loader, figlet_font, display_width, line_spacing)
        elif ascii_art or simple_ascii:
            _handle_ascii_art(loader, output, display_width, simple_ascii)
        elif display:
            _handle_display(loader, output, resize)
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
