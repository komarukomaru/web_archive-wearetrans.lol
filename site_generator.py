import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from data_parser import parse_data


def clean_build(build_dir):
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)


def copy_file(src, dst):
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def render_and_write(env, template_name, context, output_path):
    template = env.get_template(template_name)
    html = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def generate_site(data_dir=None, build_dir=None):
    if data_dir is None:
        data_dir = Path("data")
    else:
        data_dir = Path(data_dir)

    if build_dir is None:
        build_dir = Path("build")
    else:
        build_dir = Path(build_dir)

    artists = parse_data(data_dir)

    clean_build(build_dir)

    static_src = Path("static")
    if static_src.is_dir():
        shutil.copytree(static_src, build_dir / "static")

    env = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    render_and_write(env, "index.html", {
        "artists": artists,
        "base_path": "",
    }, build_dir / "index.html")

    for artist in artists:
        artist_dir = build_dir / artist["slug"]
        artist_dir.mkdir(parents=True, exist_ok=True)

        if artist["avatar"]:
            copy_file(
                data_dir / artist["slug"] / artist["avatar"],
                artist_dir / artist["avatar"],
            )

        render_and_write(env, "artist.html", {
            "artist": artist,
            "base_path": "../",
        }, artist_dir / "index.html")

        for album in artist["albums"]:
            album_dir = artist_dir / album["slug"]
            album_dir.mkdir(parents=True, exist_ok=True)

            if album["cover"]:
                copy_file(
                    data_dir / artist["slug"] / album["slug"] / album["cover"],
                    album_dir / album["cover"],
                )

            for track in album["tracks"]:
                copy_file(
                    data_dir / artist["slug"] / album["slug"] / track["file"],
                    album_dir / track["file"],
                )

            tracks_json = json.dumps(album["tracks"], ensure_ascii=False)

            render_and_write(env, "album.html", {
                "artist": artist,
                "album": album,
                "tracks_json": tracks_json,
                "base_path": "../../",
            }, album_dir / "index.html")

    total_tracks = sum(
        len(track)
        for artist in artists
        for track in [album["tracks"] for album in artist["albums"]]
    )

    print(f"build complete: {len(artists)} artists, "
          f"{sum(len(a['albums']) for a in artists)} albums, "
          f"{total_tracks} tracks")
    print(f"output: {build_dir.resolve()}")


if __name__ == "__main__":
    generate_site()
