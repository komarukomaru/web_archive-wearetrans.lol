import json
import re
from pathlib import Path


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def humanize_name(dirname):
    name = re.sub(r"^\d+_", "", dirname)
    return name.replace("_", " ").title()


def find_image(directory, prefix):
    for ext in IMAGE_EXTENSIONS:
        candidate = directory / f"{prefix}{ext}"
        if candidate.is_file():
            return candidate.name
    return None


def read_description(directory):
    desc_file = directory / "description.txt"
    if desc_file.is_file():
        return desc_file.read_text(encoding="utf-8").strip()
    return ""


def parse_album(album_dir):
    tracks = []
    for item in sorted(album_dir.iterdir()):
        if item.is_file() and item.suffix.lower() == ".mp3":
            tracks.append({
                "name": humanize_name(item.stem),
                "file": item.name,
            })

    return {
        "name": humanize_name(album_dir.name),
        "slug": album_dir.name,
        "description": read_description(album_dir),
        "cover": find_image(album_dir, "album_cover"),
        "tracks": tracks,
    }


def parse_artist(artist_dir):
    albums = []
    for item in sorted(artist_dir.iterdir()):
        if item.is_dir():
            albums.append(parse_album(item))

    return {
        "name": humanize_name(artist_dir.name),
        "slug": artist_dir.name,
        "description": read_description(artist_dir),
        "avatar": find_image(artist_dir, "avatar"),
        "albums": albums,
    }


def parse_data(data_dir=None):
    if data_dir is None:
        data_dir = Path("data")
    else:
        data_dir = Path(data_dir)

    artists = []
    if not data_dir.is_dir():
        return artists

    for item in sorted(data_dir.iterdir()):
        if item.is_dir():
            artists.append(parse_artist(item))

    return artists


if __name__ == "__main__":
    result = parse_data()
    print(json.dumps(result, indent=2, ensure_ascii=False))
