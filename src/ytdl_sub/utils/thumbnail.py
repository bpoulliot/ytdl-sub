import os
import tempfile
from typing import Optional
from urllib.request import urlopen

from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.retry import retry


class ThumbnailTypes:
    LATEST_ENTRY = "latest_entry"


def convert_download_thumbnail(entry: Entry, error_if_not_found: bool = True) -> None:
    """
    Converts an entry's downloaded thumbnail into jpg format

    Parameters
    ----------
    entry
        Entry with the thumbnail
    error_if_not_found
        If the thumbnail is not found, error if True.

    Raises
    ------
    ValueError
        Entry thumbnail file not found
    """
    download_thumbnail_path = entry.get_ytdlp_download_thumbnail_path()
    download_thumbnail_path_as_jpg = entry.get_download_thumbnail_path()

    # If it was already converted, do not convert again
    if os.path.isfile(download_thumbnail_path_as_jpg):
        return

    if not download_thumbnail_path:
        if error_if_not_found:
            raise ValueError("Thumbnail not found")
        return

    if not download_thumbnail_path == download_thumbnail_path_as_jpg:
        FFMPEG.run(["-bitexact", "-i", download_thumbnail_path, download_thumbnail_path_as_jpg])


@retry(times=5, exceptions=(Exception,))
def convert_url_thumbnail(thumbnail_url: str, output_thumbnail_path: str) -> Optional[bool]:
    """
    Downloads and converts a thumbnail from a url into a jpg

    Parameters
    ----------
    thumbnail_url
        URL of the thumbnail
    output_thumbnail_path
        Thumbnail file destination after its converted to jpg

    Returns
    -------
    True to indicate it converted the thumbnail from url. None if the retry failed.
    """
    with urlopen(thumbnail_url) as file:
        with tempfile.NamedTemporaryFile() as thumbnail:
            thumbnail.write(file.read())

            FFMPEG.run(["-bitexact", "-i", thumbnail.name, output_thumbnail_path, "-bitexact"])

    return True
