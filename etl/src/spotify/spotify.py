from abc import ABC, abstractmethod
from logging import Logger

from requests import Session, HTTPError
from requests.adapters import HTTPAdapter, Retry
from base64 import b64encode
from datetime import datetime
import pytz

from src.utils.custom_logger import init_logger
from src.utils.helper import iter_execute, write_json
from src.mapping.custom_types import IngegratedSongMetadata, IntegratedArtistMetadata
from src.msd.custom_types import MsdArtist, MsdSong
from src.spotify.custom_types import SpotifySong, SpotifyArtist
from src.mapping.custom_types import MappedSong, MappedArtist


class SpotifyClient:
    def __init__(self, client_id, client_secret, logger: Logger = None):

        self.logger = logger or init_logger(self.__class__.__name__)
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
        """Initiate a session to interact with Spotify's API server 

        Parameters
        ----------
        total_retry : int, optional
            Total number of retries allowed, by default 5
        backoff_factor : int, optional
            This is used to calculate the wait time applied between each retry. 
            The formula is: {backoff_factor} * 2^({total_retry} - 1)
            For example, with backof_factor = 1, total_retry = 5, the wait times will be
            [1, 2, 4, 8, 16]
        status_forcelist : list[int], optional
            List of status code that we will enforce retries, by default [500, 502, 503, 504, 429]

        Returns
        -------
        Session
        """
        session = Session()
        retries_strategy = Retry(total=total_retry, 
                                backoff_factor=backoff_factor, 
                                status_forcelist=status_forcelist)
        session.mount('https://', HTTPAdapter(max_retries=retries_strategy))
        return session

    def authenticate(self):
        """Authenticate the client. Steps:
        - Send a POST request to generate an access token
        - Add the access token to the header of the session.

        Raises
        ------
        """
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
        """Check if the access token is still in valid time time. if not, regenerate the access token.
        """
        if (datetime.now(pytz.utc) - self.access_token_created_at).total_seconds() >= 3600:
            self.authenticate()

    def check_connection(self):
        """Check if the client can connect to Spotify's server
        """
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
    """Abstract class for various fetchers"""

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
            return None
        else:
            return response.json()

    def output_json(
            self, 
            data: list[MappedArtist | MappedSong | SpotifyArtist | SpotifySong], 
            output_path: str,
            new_line_delimited: bool = False
        ):
        write_json(data, output_path, new_line_delimited, self.logger)
        
                
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

    def search_one(self, msd_song: MsdSong, limit=10) -> MappedSong:
        """Receive a MsdSong object and search for the song in Spotify by using its name and artist.

        Parameters
        ----------
        msd_song : MsdSong
            MsdSong object
        limit : int, optional
            Maximum number of songs to be returned, by default 10

        Returns
        -------
        MappedSong
            An object represent the search result
        """        
        self.client.check_authentication()

        params = {
            'q': f"track:{msd_song.name} artist:{msd_song.artist_name}",
            'type': 'track',
            'limit': limit
        }

        result = self._fetch_data(self.search_url, params)
        if result is not None:
            matched_results = {
                'msd_song_id': msd_song.id,
                'spotify_song_ids': [i['id'] for i in result['tracks']['items']]
            }
            return MappedSong(**matched_results)
        else:
            return None
    
    def search_many(self, msd_songs_list: list[MsdSong]) -> list[MappedSong]:
        """Iterate through the list of MsdSong objects and return a list of MappedSong objects

        Parameters
        ----------
        msd_songs : list[MsdSong]

        Returns
        -------
        list[MappedSong]
        """

        # TODO: Implement rate limit

        results = iter_execute(
            func=self.search_one, 
            iterable=msd_songs_list, 
            logger=self.logger,
            logging_interval=10,
            message_template="Processed {} of {} songs ({}%)"
        )

        return results

    def fetch_one(self, spotify_song_id: str) -> dict:
        """Fetch one song from Spotify using the Spotify Song ID provided.

        Parameters
        ----------
        spotify_song_id : str

        Returns
        -------
        dict
            dict containing one song info
        """
        self.client.check_authentication()
        params = {"ids": spotify_song_id}
        result = self._fetch_data(self.fetch_url, params)
        return result

    def fetch_many(self, mapped_songs: list[MappedSong]) -> list[SpotifySong]:
        """Iterate through the list of MappedSong objects, and return full song metadata, including
        both the MSD song ID and the Spotify song metadata

        Parameters
        ----------
        mapped_songs : list[MappedSong]

        Returns
        -------
        list[IngegratedSongMetadata]
        """

        def fetch_func(item: MappedSong) -> list:
            result = []

            if len(item.spotify_song_ids) > 0:
            
                params = {'ids': ','.join(item.spotify_song_ids)}
                fetch_results = self._fetch_data(self.fetch_url, params)

                for track in fetch_results['tracks']:
                    data = {
                        'id'                : track['id'],
                        'name'              : track['name'],
                        'url'               : track['external_urls']['spotify'],
                        'external_ids'      : track['external_ids'],
                        'popularity'        : track['popularity'],
                        'available_markets' : track['available_markets'],
                        'album_id'          : track['album']['id'],
                        'artists'           : [{'artist_id': artist['id'], 'artist_name': artist['name']}
                                                for artist in track['artists']],
                        'duration_ms'       : track['duration_ms']
                    }
                    result.append(SpotifySong(**data))

            return result
        
        results = iter_execute(
            func=fetch_func, 
            iterable=mapped_songs, 
            logger=self.logger,
            logging_interval=10,
            message_template="Processing {} of {} songs ({}))"
        )

        return results


class ArtistFetcher(BaseFetcher):

    def __init__(self, client: SpotifyClient, logger: Logger = None) -> None:
        super().__init__(client, logger)
        self.search_url = "https://api.spotify.com/v1/search"
        self.fetch_url = "https://api.spotify.com/v1/artists"

    def search_one(self, msd_artist: MsdArtist, limit=10) -> MappedArtist:
        """Receive a MsdArtist object and search for the artist in Spotify.

        Parameters
        ----------
        msd_artist : MsdArtist
        limit : int, optional
            Maximum number of artists to be returned, by default 10

        Returns
        -------
        MappedArtist
        """
        self.client.check_authentication()

        params = {
            'q': f"artist:{msd_artist.name}",
            'type': 'artist',
            'limit': limit
        }

        result = self._fetch_data(self.search_url, params)
        
        if result is not None:
            matched_results = {
                'msd_artist_id': msd_artist.id,
                'spotify_artist_ids': [i['id'] for i in result['artists']['items']]
            }
            return MappedArtist(**matched_results)
        else:
            return None

    def search_many(self, msd_artists_list: list[MsdArtist]) -> list[MappedArtist]:
        """Iterate through the list of MsdArtist objects and return a list of MappedArtist objects    

        Parameters
        ----------
        msd_artists_list : list[MsdArtist]

        Returns
        -------
        list[MappedArtist]
        """

        results = iter_execute(
            func=self.search_one, 
            iterable=msd_artists_list,
            logger=self.logger,
            logging_interval=10,
            message_template="Processed {} of {} artists ({}%)"
        )
        return results

    def fetch_one(self, spotify_artist_id: str) -> dict:
        """Fetch one artist from Spotify using the artist's Spotify ID

        Parameters
        ----------
        spotify_artist_id : str

        Returns
        -------
        dict
            dict containing info about one artist
        """
        self.client.check_authentication()
        params = {"ids": spotify_artist_id}
        result = self._fetch_data(self.fetch_url, params)
        return result

    def fetch_many(self, artist_search_results: list[MappedArtist]) -> list[SpotifyArtist]:
        """Iterate through the list of MappedArtist objects and return a list of IntegratedArtistMetadata,
        containing both data from MSD and Spotify    

        Parameters
        ----------
        artist_search_results : list[MappedArtist]

        Returns
        -------
        list[IntegratedArtistMetadata]
        """
        def fetch_func(item: MappedArtist) -> list:
            
            result = []

            if len(item.spotify_artist_ids) > 0:

                params = {"ids": ','.join(item.spotify_artist_ids)}
                fetch_results = self._fetch_data(self.fetch_url, params)

                for artist in fetch_results['artists']:
                    data = {
                        'id'                : artist['id'],
                        'name'              : artist['name'],
                        'url'               : artist['external_urls']['spotify'],
                        'total_followers'   : artist['followers']['total'],
                        'popularity'        : artist['popularity'],
                        'genres'            : artist['genres'],
                    }
                    result.append(SpotifyArtist(**data))

            return result

        results = iter_execute(
            func=fetch_func, 
            iterable=artist_search_results,
            logger=self.logger,
            logging_interval=10,
            message_template="Processing {} of total {} artists ({}%)"
        )

        return results
    

class AlbumFetcher():
    pass

class AudioFeaturesFetcher():
    pass