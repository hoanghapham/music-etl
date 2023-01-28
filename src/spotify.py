from abc import ABC, abstractmethod
from logging import Logger
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from src.utils.custom_logger import init_logger
from src

class SpotifyClient(Spotify):
    def __init__(self, client_id, client_secret):
        cred = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        super().__init__(client_credentials_manager=cred)


class BaseFetcher(ABC):

    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        self.client = client
        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger

    @abstractmethod
    def search_one(self):
        pass

    @abstractmethod
    def search_many(self):
        pass


class SongFetcher(BaseFetcher):

    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        super().__init__(client, logger)

    def search_one(self, mds_song, limit=10):
        query = f"track:{song_name} artist:{artist_name}"
        result = self.client.search(q=query, type='track', limit=limit)

        tracks = result['tracks']['items']
        result_names = [i['name'] for i in tracks]
        # self.logger.info(f"Found {result['tracks']['total']} track(s): {'; '.join(result_names)}")
        
        return tracks
    
    def search_many(self, mds_song_list):

        # TODO: Implement rate limit
        tracks = []

        for song_name, artist_name in mds_song_list:
            result = self.search_one(song_name, artist_name)
            tracks += result

        self.logger.info(f"Found {len(tracks)} track(s)")

        return tracks

    def fetch_many(self, song_id_list):

        result = self.client.tracks(song_id_list)
        tracks = []

        for track in result['tracks']:
            if track is not None:
                data = {
                    'id'                : track['id'],
                    'name'              : track['name'],
                    'url'               : track['external_urls']['spotify'],
                    'external_ids'      : track['external_ids'],
                    'popularity'        : track['popularity'],
                    'available_markets' : track['available_markets'],
                    'album'             : [album['id'] for album in track['albumn']],
                    'artists'           : [{'artist_id': artist['id'], 'artist_name': artist['name']}
                                            for artist in track['artists']],
                    'duration_ms'       : track['duration_ms']
                }
                track.append(data)

        self.logger.info(f"Fetched {len(tracks)}/{len(song_id_list)} songs.")
        return tracks


class ArtistFetcher(BaseFetcher):

    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        super().__init__(client, logger)

    def search_one(self, artist_name, limit=10):
        query = f"artist:{artist_name}"
        result = self.client.search(q=query, type='artist', limit=limit)

        artists = result['artists']['items']
        result_names = [i['name'] for i in artists]

        # self.logger.info(f"Found {result['artists']['total']} artist(s): {'; '.join(result_names)}")
        
        return artists

    def search_many(self, mds_artist_list):
        artists = []

        for artist_name in mds_artist_list:
            result = self.search_one(artist_name)
            artists += result

        self.logger.info(f"Found {len(artists)} artist(s)")
        return artists

    def fetch_many(self, artist_id_list):

        result = self.client.artists(artist_id_list)

        artists = []

        for artist in result['artists']:
            if artist is not None:
                data = {
                    'url'               : artist['external_urls']['spotify'],
                    'total_followers'   : artist['followeres']['total'],
                    'id'                : artist['id'],
                    'name'              : artist['name'],
                    'popularity'        : artist['popularity'],
                    'genres'            : artist['genres'],
                }
                artists.append(data)

        self.logger.info(f"Fetched {len(artists)}/{len(artist_id_list)} artists.")
        return artists
    

class AlbumFetcher():
    pass
