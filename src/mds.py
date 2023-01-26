import tables
import json
import glob
from src.utils.custom_logger import init_logger
from abc import ABC, abstractmethod
from logging import Logger


class BaseExtractor(ABC):
    
    @abstractmethod
    def __init__(self, logger: Logger = None) -> None:

        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger

    @abstractmethod
    def extract_one(self, input_path: str) -> dict:
        pass
    
    def extract_many(self, input_path: str):
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

    def output_json(self, data, output_path):
        if len(data) == 0:
            self.logger.info(f"No data to write.")
        else:
            with open(output_path, 'w') as f:
                json.dump(data, f)


class SongsExtractor(BaseExtractor):
    def __init__(self, logger: Logger = None) -> None:
        super().__init__(logger)

    def extract_one(self, file_path):

        with tables.open_file(file_path, 'r') as f:
            nrows = f.root.metadata.songs.nrows

            for row in range(nrows):
                song_id = f.root.metadata.songs.cols.song_id[row].decode('utf-8')
                title = f.root.metadata.songs.cols.title[row].decode('utf-8')
                release = f.root.metadata.songs.cols.release[row].decode('utf-8')
                genre = f.root.metadata.songs.cols.genre[row].decode('utf-8')
                artist_id = f.root.metadata.songs.cols.artist_id[row].decode('utf-8')
                year = int(f.root.musicbrainz.songs.cols.year[row])

                data = {
                    'id': song_id,
                    'title': title,
                    'release': release,
                    'genre': genre,
                    'artist_id': artist_id,
                    'year': year
                }

        return data

class ArtistsExtractor(BaseExtractor):
    def __init__(self, logger: Logger = None) -> None:
        super().__init__(logger)

    def extract_one(self, input_path: str) -> dict:
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
        
        return data