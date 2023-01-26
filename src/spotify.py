
from logging import Logger
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from src.utils.custom_logger import init_logger


class SpotifyClient(Spotify):
    def __init__(self, client_id, client_secret):
        cred = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        super().__init__(client_credentials_manager=cred)


class SongSearcher():
    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        self.client = client
        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger

    def search_one(self, song_name, artist_name, type='track', limit=10):
        query = f"track:{song_name} artist:{artist_name}"
        result = self.client.search(q=query, type=type, limit=limit)

        tracks = result['tracks']['items']
        result_names = [i['name'] for i in tracks]

        self.logger.info(f"Found {result['tracks']['total']} track(s): {'; '.join(result_names)}")
        
        return tracks
    
    def search_many(self, song_dict):
        # Need to implement rate limit
        pass


class ArtistSearcher():
    pass

class AlbumnSearcher():
    pass
