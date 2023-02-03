from abc import ABC, abstractmethod
from logging import Logger
import glob
import tables
import numpy as np

from src.utils.custom_logger import init_logger
from src.utils.helper import iter_execute, write_json
from src.msd.custom_types import MsdSong, MsdArtist

class BaseExtractor(ABC):
    """Abstract class for MSD dataset extractors"""
    
    @abstractmethod
    def __init__(self, logger: Logger = None) -> None:
        self.logger = logger or init_logger(self.__class__.__name__)

    @abstractmethod
    def extract_one_file(self, input_path: str) -> dict:
        pass
    
    def extract_many_files(self, input_path: str) -> list[MsdSong] | list[MsdArtist]:
        """Iterate through the files in the input path and extract multiple objects

        Parameters
        ----------
        input_path : str
            Input file path with '*' patterns that signify multiple files.

        Returns
        -------
        list[MsdSong] | list[MsdArtist]
            List of MsdSong objects or MsdArtist objects
        """
        self.input_path = input_path
        self.file_paths = glob.glob(self.input_path, recursive=True)
        self.num_files = len(self.file_paths)
        self.logger.info(f"Found {self.num_files} files")

        if self.num_files == 0:
            data = []

        else:
            data = iter_execute(
                func=self.extract_one_file, 
                iterable=self.file_paths, 
                logger=self.logger,
            )

        return data

    def output_json(
            self, 
            data: list[MsdSong | MsdArtist] | MsdSong | MsdArtist, 
            output_path: str,
            new_line_delimited: bool = True
        ):
        """Write a JSON representation of the objects

        Parameters
        ----------
        data : list[MsdSong] | list[MsdArtist]
            Input MsdSong or MsdArtist objects
        output_path : str
            Full destination path.
        new_line_delimited : bool
            if True, write JSON in new-line delimited format
        """
        write_json(data, output_path, new_line_delimited, self.logger)
                        

class SongExtractor(BaseExtractor):
    def __init__(self, logger: Logger = None) -> None:
        super().__init__(logger)

    def extract_one_file(self, file_path: str) -> list[MsdSong]:
        """Extract song data from one MSD's H5 file and

        Parameters
        ----------
        file_path : str
            Path to one H5 file

        Returns
        -------
        MsdSong
            An object representing a song extracted from MSD dataset
        """

        with tables.open_file(file_path, 'r') as file:

            def extract_func(row):
                song_id = file.root.metadata.songs.cols.song_id[row].decode('utf-8')
                name = file.root.metadata.songs.cols.title[row].decode('utf-8')
                release = file.root.metadata.songs.cols.release[row].decode('utf-8')
                genre = file.root.metadata.songs.cols.genre[row].decode('utf-8')
                artist_id = file.root.metadata.songs.cols.artist_id[row].decode('utf-8')
                artist_name = file.root.metadata.songs.cols.artist_name[row].decode('utf-8')
                year = int(file.root.musicbrainz.songs.cols.year[row])

                data = {
                    'id': song_id,
                    'name': name,
                    'release': release,
                    'genre': genre,
                    'artist_id': artist_id,
                    'artist_name': artist_name,
                    'year': year
                }
                return MsdSong(**data)

            nrows = file.root.metadata.songs.nrows
            result = iter_execute(extract_func, range(nrows))

        return result

class ArtistExtractor(BaseExtractor):
    def __init__(self, logger: Logger = None) -> None:
        super().__init__(logger)

    def extract_one_file(self, input_path: str) -> MsdArtist:
        """Extract artist data from one MSD's H5 file

        Parameters
        ----------
        input_path : str
            Path to one H5 file

        Returns
        -------
        MsdArtist
            An object representing a song extracted from MSD dataset
        """

        with tables.open_file(input_path, 'r') as file:

            def extract_func(row):            
                id = file.root.metadata.songs.cols.artist_id[row].decode('utf-8')
                name = file.root.metadata.songs.cols.artist_name[row].decode('utf-8')
                location = file.root.metadata.songs.cols.artist_location[row].decode('utf-8')
                latitude = file.root.metadata.songs.cols.artist_latitude[row]
                longitude = file.root.metadata.songs.cols.artist_longitude[row]
                terms = [i.decode('utf-8') for i in list(file.root.metadata.artist_terms)]

                data = {
                    'id': id,
                    'name': name,
                    'location': location,
                    'latitude': None if np.isnan(latitude) else latitude,
                    'longitude': None if np.isnan(longitude) else longitude,
                    'tags': terms
                }
                return MsdArtist(**data)

            nrows = file.root.metadata.songs.nrows
            result = iter_execute(extract_func, range(nrows))
        
        return result
