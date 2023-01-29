from abc import ABC, abstractmethod
from logging import Logger

from requests import Session, HTTPError
from requests.adapters import HTTPAdapter, Retry
from base64 import b64encode
from datetime import datetime
import pytz

from src.utils.custom_logger import init_logger
from src.custom_types import (
    MdsArtist, 
    MdsSong, 
    SpotifySong,
    SpotifyArtist,
    SongSearchResult,
    ArtistSearchResult,
    IngegratedSongMetadata,
    IntegratedArtistMetadata
)
from src.utils.helpers import generate_logging_points


class SpotifyClient:
    def __init__(self, client_id, client_secret, logger: Logger = None):

        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger
        
        self.auth_url = 'https://accounts.spotify.com/api/token'
        self.client_id = client_id
        self.client_secret = client_secret

        self.session = self.get_session()
        self.authenticate()
        self.check_connection()

    def get_session(
            self, 
            total_retry: int = 5,
            backoff_factor: int = 1,
            status_forcelist: list[int] = [500, 502, 503, 504, 429]
        ) -> Session:
        session = Session()
        retries_strategy = Retry(total=total_retry, 
                                backoff_factor=backoff_factor, 
                                status_forcelist=status_forcelist)
        session.mount('https://', HTTPAdapter(max_retries=retries_strategy))
        return session

    def authenticate(self):
        auth_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': "Basic " + b64encode(f"{self.client_id}:{self.client_secret}".encode('ascii')).decode('utf-8')
        }
        auth_body = {'grant_type': 'client_credentials'}

        response = self.session.post(url=self.auth_url, headers=auth_headers, data=auth_body)
        self.access_token_created_at = datetime.now(pytz.utc)

        try:
            response.raise_for_status()
        except HTTPError as e:
            self.logger.error(e)
            raise e
        else:
            self.access_token = response.json()['access_token']
            self.session.headers.update({
                "Accept": "application/json" ,
                "Content-Type": "application/json", 
                "Authorization": "Bearer " + self.access_token
            })
            self.logger.info("Generated new access token")

    def check_authentication(self):
        if (datetime.now(pytz.utc) - self.access_token_created_at).total_seconds() >= 3600:
            self.authenticate()

    def check_connection(self):
        url = "https://api.spotify.com/v1/tracks/4cOdK2wGLETKBW3PvgPWqT"
        response = self.session.get(url)
        try:
            response.raise_for_status()
        except HTTPError as e:
            self.logger.error("Cannot connect to Spotify server")
            self.logger.error(response.json()['error']['message'])
            raise e
        else:
            self.logger.info("Connected to Spotify server successfully.")


class BaseFetcher(ABC):

    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        self.client = client
        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger
    
    def _fetch_data(self, url, params):
        response = self.client.session.get(url=url, params=params)
        try:
            response.raise_for_status()
        except HTTPError as e:
            self.logger.error(e)
            raise e
        else:
            return response.json()

    @abstractmethod
    def search_one(self):
        pass

    @abstractmethod
    def search_many(self):
        pass

    @abstractmethod
    def fetch_one(self):
        pass

    @abstractmethod
    def fetch_many(self):
        pass

class SongFetcher(BaseFetcher):

    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        super().__init__(client, logger)
        self.search_url = "https://api.spotify.com/v1/search"
        self.fetch_url = "https://api.spotify.com/v1/tracks"

    def search_one(self, mds_song: MdsSong, limit=10) -> SongSearchResult:
        self.client.check_authentication()

        params = {
            'q': f"track:{mds_song.title} artist:{mds_song.artist_name}",
            'type': 'track',
            'limit': limit
        }

        result = self._fetch_data(self.search_url, params)
        matched_results = {
            'mds_song_id': mds_song.id,
            'spotify_song_ids': [i['id'] for i in result['tracks']['items']]
        }
        return SongSearchResult.parse_obj(matched_results)
    
    def search_many(self, mds_songs: list[MdsSong]) -> list[SongSearchResult]:

        # TODO: Implement rate limit
        results = []
        total = len(mds_songs)
        logging_point = generate_logging_points(total)
        total_found = 0

        for i, song in enumerate(mds_songs):
            result = self.search_one(song)
            results.append(SongSearchResult.parse_obj(result))
            total_found += len(result.spotify_song_ids)

            if i in logging_point:
                self.logger.info(f"Processed {i} of {total} songs ({round(i / total * 100, 2)}%)")

        self.logger.info(f"Total found: {total_found} track(s)")
        return results

    def fetch_one(self, spotify_song_id: str):
        self.client.check_authentication()
        params = {"ids": spotify_song_id}
        result = self._fetch_data(self.fetch_url, params)
        return result

    def fetch_many(self, song_search_results: list[SongSearchResult]) -> list[IngegratedSongMetadata]:
        
        results = []
        total = len(song_search_results)
        logging_points = generate_logging_points(total)

        for i, item in enumerate(song_search_results):
            if i in logging_points:
                self.logger.info(f"Processing {i} of {total} songs ({round(i / total * 100, 2)}%)")

            if len(item.spotify_song_ids) > 0:
            
                spotify_results = []
                params = {'ids': ','.join(item.spotify_song_ids)}
                result = self._fetch_data(self.fetch_url, params)

                for track in result['tracks']:
                    data = {
                        'id'                : track['id'],
                        'name'              : track['name'],
                        'url'               : track['external_urls']['spotify'],
                        'external_ids'      : track['external_ids'],
                        'popularity'        : track['popularity'],
                        'available_markets' : track['available_markets'],
                        'album'             : track['album']['id'],
                        'artists'           : [{'artist_id': artist['id'], 'artist_name': artist['name']}
                                                for artist in track['artists']],
                        'duration_ms'       : track['duration_ms']
                    }
                    spotify_results.append(SpotifySong.parse_obj(data))
            
                results.append(IngegratedSongMetadata.parse_obj(
                    {'mds_song_id': item.mds_song_id, 'spotify_songs': spotify_results}))

        return results


class ArtistFetcher(BaseFetcher):

    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        super().__init__(client, logger)
        self.search_url = "https://api.spotify.com/v1/search"
        self.fetch_url = "https://api.spotify.com/v1/artists"

    def search_one(self, mds_artist: MdsArtist, limit=10):
        self.client.check_authentication()

        params = {
            'q': f"artist:{mds_artist.name}",
            'type': 'artist',
            'limit': limit
        }

        result = self._fetch_data(self.search_url, params)
        matched_results = {
            'mds_artist_id': mds_artist.id,
            'spotify_artist_ids': [i['id'] for i in result['artists']['items']]
        }
        return ArtistSearchResult.parse_obj(matched_results)

    def search_many(self, mds_artist_list):
        results = []
        total = len(mds_artist_list)
        logging_points = generate_logging_points(total)
        total_found = 0

        for i, artist_name in enumerate(mds_artist_list):
            result = self.search_one(artist_name)
            results.append(ArtistSearchResult.parse_obj(result))
            total_found += len(result.spotify_artist_ids)

            if i in logging_points:
                self.logger.info(f"Processed {i} of {total} artists ({round(i / total * 100, 2)}%)")

        self.logger.info(f"Total found: {total_found} artist(s)")
        return results

    def fetch_one(self, spotify_artist_id: str):
        self.client.check_authentication()
        params = {"ids": spotify_artist_id}
        result = self._fetch_data(self.fetch_url, params)
        return result

    def fetch_many(self, artist_search_results: list[ArtistSearchResult]) -> list[IntegratedArtistMetadata]:

        results = []
        total = len(artist_search_results)
        logging_points = generate_logging_points(total)

        for i, item in enumerate(artist_search_results):
            if i in logging_points:
                self.logger.info(f"Processing {i} of total artists ({round(i / total * 100, 2)}%)")

            if len(item.spotify_artist_ids) > 0:

                spotify_results = []
                params = {"ids": ','.join(item.spotify_artist_ids)}
                result = self._fetch_data(self.fetch_url, params)

                for artist in result['artists']:
                    data = {
                        'id'                : artist['id'],
                        'name'              : artist['name'],
                        'url'               : artist['external_urls']['spotify'],
                        'total_followers'   : artist['followers']['total'],
                        'popularity'        : artist['popularity'],
                        'genres'            : artist['genres'],
                    }
                    spotify_results.append(SpotifyArtist.parse_obj(data))
                
                results.append(IntegratedArtistMetadata.parse_obj(
                    {'mds_artist_id': item.mds_artist_id, 'spotify_artists': spotify_results}))

        return results
    

class AlbumFetcher():
    pass
