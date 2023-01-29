from abc import ABC, abstractmethod
from logging import Logger
import json
import glob
import tables
from pydantic import parse_obj_as

from src.utils.custom_logger import init_logger
from src.custom_types import MdsSong, MdsArtist

class BaseExtractor(ABC):
    """Abstract class for MDS dataset extractors"""
    
    @abstractmethod
    def __init__(self, logger: Logger = None) -> None:

        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger

    @abstractmethod
    def extract_one(self, input_path: str) -> dict:
        pass
    
    def extract_many(self, input_path: str) -> list[MdsSong] | list[MdsArtist]:
        """Iterate through the files in the input path and extract multiple objects

        Parameters
        ----------
        input_path : str
            Input file path with '*' patterns that signify multiple files.

        Returns
        -------
        list[MdsSong] | list[MdsArtist]
            List of MdsSong objects or MdsArtist objects
        """
        self.input_path = input_path
        self.file_paths = glob.glob(self.input_path)
        self.num_files = len(self.file_paths)
        self.logger.info(f"Found {self.num_files} files")

        data = []
        logging_points = [round(i/100 * self.num_files) for i in range(20, 120, 20)]

        for i, path in enumerate(self.file_paths, start=1):
            data.append(self.extract_one(path))

            if i in logging_points:
                self.logger.info(f"Processed {i} files of {self.num_files} ({round(i / self.num_files * 100)}%)")
        
        return data

    def output_json(self, data: list[MdsSong] | list[MdsArtist], output_path: str):
        """Write a JSON representation of the objects

        Parameters
        ----------
        data : list[MdsSong] | list[MdsArtist]
            Input MdsSong or MdsArtist objects
        output_path : str
            Full destination path.
        """
        if len(data) == 0:
            self.logger.info(f"No data to write.")
        else:
            json_data = [i.dict() for i in data]
            with open(output_path, 'w') as f:
                json.dump(json_data, f)


class SongExtractor(BaseExtractor):
    def __init__(self, logger: Logger = None) -> None:
        super().__init__(logger)

    def extract_one(self, file_path: str) -> MdsSong:
        """Extract song data from one MDS's H5 file and

        Parameters
        ----------
        file_path : str
            Path to one H5 file

        Returns
        -------
        MdsSong
            An object representing a song extracted from MDS dataset
        """

        with tables.open_file(file_path, 'r') as f:
            nrows = f.root.metadata.songs.nrows

            for row in range(nrows):
                song_id = f.root.metadata.songs.cols.song_id[row].decode('utf-8')
                title = f.root.metadata.songs.cols.title[row].decode('utf-8')
                release = f.root.metadata.songs.cols.release[row].decode('utf-8')
                genre = f.root.metadata.songs.cols.genre[row].decode('utf-8')
                artist_id = f.root.metadata.songs.cols.artist_id[row].decode('utf-8')
                artist_name = f.root.metadata.songs.cols.artist_name[row].decode('utf-8')
                year = int(f.root.musicbrainz.songs.cols.year[row])

                data = {
                    'id': song_id,
                    'title': title,
                    'release': release,
                    'genre': genre,
                    'artist_id': artist_id,
                    'artist_name': artist_name,
                    'year': year
                }

        return parse_obj_as(MdsSong, data)

class ArtistExtractor(BaseExtractor):
    def __init__(self, logger: Logger = None) -> None:
        super().__init__(logger)

    def extract_one(self, input_path: str) -> MdsArtist:
        """Extract artist data from one MDS's H5 file

        Parameters
        ----------
        input_path : str
            Path to one H5 file

        Returns
        -------
        MdsArtist
            An object representing a song extracted from MDS dataset
        """
        with tables.open_file(input_path, 'r') as f:
            nrows = f.root.metadata.songs.nrows

            for row in range(nrows):
                artist_id = f.root.metadata.songs.cols.artist_id[row].decode('utf-8')
                artist_name = f.root.metadata.songs.cols.artist_name[row].decode('utf-8')
                artist_location = f.root.metadata.songs.cols.artist_location[row].decode('utf-8')
                artist_terms = [i.decode('utf-8') for i in list(f.root.metadata.artist_terms)]

                data = {
                    'id': artist_id,
                    'name': artist_name,
                    'location': artist_location,
                    'tags': artist_terms
                }
        
        return parse_obj_as(MdsArtist, data)
