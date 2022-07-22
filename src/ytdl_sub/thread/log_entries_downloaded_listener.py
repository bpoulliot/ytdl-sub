import json
import os.path
import threading
import time
from pathlib import Path
from typing import Optional
from typing import Set

from ytdl_sub.utils.logger import Logger

logger = Logger.get(name="downloader")


class LogEntriesDownloadedListener(threading.Thread):
    def __init__(self, working_directory, info_json_extractor):
        """
        To be ran in a thread while download via ytdl-sub. Listens for new .info.json files in the
        working directory, checks the extractor value, and if it matches the input arg, log the
        title.

        Parameters
        ----------
        working_directory
            subscription download working directory
        info_json_extractor
            print the titles of the info.json file with this extractor
        """
        threading.Thread.__init__(self)
        self.working_directory = working_directory
        self.info_json_extractor = info_json_extractor
        self.complete = False

        self._files_read: Set[str] = set()

    def _get_title_from_info_json(self, path: Path) -> Optional[str]:
        with open(path, "r", encoding="utf-8") as file:
            file_json = json.load(file)

        if file_json.get("extractor") == self.info_json_extractor:
            return file_json.get("title")

        return None

    @classmethod
    def _is_info_json(cls, path: Path) -> bool:
        if path.is_file():
            _, ext = os.path.splitext(path)
            return ext == ".json"
        return False

    def loop(self) -> None:
        """
        Read new files in the directory and print their titles
        """
        for path in Path(self.working_directory).rglob("*"):
            if path.name not in self._files_read and self._is_info_json(path):
                title = self._get_title_from_info_json(path)
                self._files_read.add(path.name)
                if title:
                    logger.info("Downloading %s", title)

    def run(self):
        """
        Loops over new files and prints their titles
        """
        while not self.complete:
            self.loop()
            time.sleep(0.1)
