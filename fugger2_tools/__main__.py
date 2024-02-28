from pathlib import Path

import typer
from construct_typed import DataclassStruct
from PIL import Image
from rich.console import Console

from fugger2_tools.const import EXTENSION_DAT
from fugger2_tools.converter import Converter
from fugger2_tools.structs import (
    Icon3,
    Icon3WithHeader,
    Icon3Write,
    IconGeneral,
    IconIN,
)

app = typer.Typer()
converter = Converter()
console = Console()


def get_files(paths: list[Path], extension: str | None = None) -> list[Path]:
    """Get all files from the provided paths."""

    files: list[Path] = []

    for path in paths:
        files.extend(_get_files(path, extension))

    files = list(set(files))
    files = sorted(files, key=lambda x: str(x))
    return files


def _get_files(path: Path, extension: str | None = None) -> set[Path]:
    """Get all files from the provided path."""

    if not path.exists():
        raise typer.BadParameter(f"Path {path} does not exist.")

    return (
        set(path.rglob("*" if extension is None else f"*.{extension}"))
        if path.is_dir()
        else set([path])
    )


@app.command()
def icons2(paths: list[Path]):
    """Process multiple paths for the icons2 command."""

    files = get_files(paths, EXTENSION_DAT)

    for file in files:
        print(f"Processing icon2 {file}")


@app.command()
def icons3(paths: list[Path]):
    """Process multiple paths for the icons3 command."""

    output_base_path = Path("./output")
    output_base_path.mkdir(exist_ok=True)

    files = get_files(paths, EXTENSION_DAT)

    for file in files:
        print(f"Processing icon3 {file}")

        output_path = output_base_path / f"{file.stem}.png"

        try:
            icon3 = DataclassStruct(Icon3).parse_file(file)
            image = converter.convert_icon3(icon3)

            if image is not None:
                image.save(output_path)
            else:
                console.print(f"Skipping {file} as it has no data.")
        except Exception:
            try:
                icon_general = DataclassStruct(IconGeneral).parse_file(file)
                image = converter.convert_icon_general(icon_general)
                image.save(output_path)
            except Exception:
                try:
                    icon_in = DataclassStruct(IconIN).parse_file(file)
                    image = converter.convert_icon_in(icon_in)
                    image.save(output_path)
                except Exception:
                    try:
                        icon3_with_header = DataclassStruct(Icon3WithHeader).parse_file(
                            file
                        )
                        image = converter.convert_icon3_with_header(icon3_with_header)
                        if image is not None:
                            image.save(output_path)
                        else:
                            console.print(f"Skipping {file} as it has no data.")
                    except Exception as e:
                        typer.echo(f"Error parsing {file}: {e}", err=True)
                        continue


@app.command()
def to_icon3(path: Path):
    if not path.exists():
        raise typer.BadParameter("File does not exist.")

    image = Image.open(path)

    icon3 = converter.convert_image_to_icon3(image)

    data = DataclassStruct(Icon3Write).build(icon3)

    with open("TEST.DAT", "wb") as f:
        f.write(data)


if __name__ == "__main__":
    app()
