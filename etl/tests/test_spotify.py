"""Unit tests for spotify module"""

import vcr
from pathlib import Path
from configparser import ConfigParser
from pytest import fixture

from src.spotify import ArtistFetcher, SongFetcher, SpotifyClient
from src.msd.custom_types import MsdArtist, MsdSong
from src.utils.custom_logger import init_logger


# Setup
p = Path(__file__).with_name('config.cfg')
config = ConfigParser()
config.read(p)

my_vcr = vcr.VCR(filter_headers=['Authorization'])
my_vcr.record_mode = 'new_episodes'
fixture_base_path = 'tests/fixtures/vcr_cassettes/spotify'

logger = init_logger(__file__)


# Test SongFetcher ----------------------------------------

@fixture
def msd_song():
    return MsdSong(
        id='SOBBUGU12A8C13E95D',
        name='Setting Fire to Sleeping Giants',
        artist_id='ARMAC4T1187FB3FA4C',
        artist_name='The Dillinger Escape Plan'
    )

@fixture
def msd_songs():
    return [
        MsdSong(
            id='SOBBUGU12A8C13E95D',
            name='Setting Fire to Sleeping Giants',
            artist_id='ARMAC4T1187FB3FA4C',
            artist_name='The Dillinger Escape Plan'
        ),
        MsdSong(
            id='SOOGFBZ12AC3DF7FF2',
            name='In A Subtle Way',
            artist_id='ARDD1RC1187B9B52B4',
            artist_name='Jacob Young',
        )
    ]

@fixture(scope='module')
def client():
    client_id       = config['SPOTIFY']['CLIENT_ID']
    client_secret   = config['SPOTIFY']['CLIENT_SECRET']
    client = SpotifyClient(client_id, client_secret)
    return client

@fixture(scope='module')
def song_fetcher(client):
    song_fetcher = SongFetcher(client)
    return song_fetcher

@fixture
@my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_search_many.yaml")
def SongFetcher_search_many(song_fetcher: SongFetcher, msd_songs: list[MsdSong]):
    result = song_fetcher.search_many(msd_songs)
    return result



class TestSongFetcher():

    @my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_search_one.yml")
    def test_search_one(self, song_fetcher: SongFetcher, msd_song: MsdSong):
        """Assert that search_one() will return data"""
        result = song_fetcher.search_one(msd_song)
        assert result is not None

    def test_search_many(self, SongFetcher_search_many):
        """Assert that search_many() will return data"""
        result = SongFetcher_search_many
        assert len(result) > 0

    @my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_fetch_one.yml")
    def test_fetch_one(self, song_fetcher: SongFetcher):
        """Assert that fetch_one() will return data of this song"""
        result = song_fetcher.fetch_one("2ZyNYdziwt0ZS9mxRiwnXM")
        assert result is not None

    @my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_fetch_many.yml")
    def test_fetch_many(self, song_fetcher: SongFetcher, SongFetcher_search_many):
        """Assert that fetch_many() will iterate through the search inputs correctly'
        and returns data"""
        result = song_fetcher.fetch_many(SongFetcher_search_many)
        assert len(result) > 0


# Test ArtistFetcher --------------------------------------------

@fixture
def artist_fetcher(client):
    return ArtistFetcher(client)

@fixture
def msd_artist():
    return MsdArtist(id='ARMJAGH1187FB546F3', name='The Box Tops')

@fixture
def msd_artists():
    return [
        MsdArtist(id='ARMJAGH1187FB546F3', name='The Box Tops'),
        MsdArtist(id='ARKRRTF1187B9984DA', name='Sonora Santanera')
    ]

@fixture
@my_vcr.use_cassette(f"{fixture_base_path}/ArtistFetcher_search_many.yaml")
def ArtistFetcher_search_many(artist_fetcher: ArtistFetcher, msd_artists):
    result = artist_fetcher.search_many(msd_artists)
    return result


class TestArtistFetcher():

    @my_vcr.use_cassette(f"{fixture_base_path}/ArtistFetcher_search_one.yaml")
    def test_search_one(self, artist_fetcher: ArtistFetcher, msd_artist):
        """Assert that search_one() will return data"""
        result = artist_fetcher.search_one(msd_artist)
        assert result is not None

    def test_search_many(self, ArtistFetcher_search_many):
        """Assert that search_many() will return data"""
        result = ArtistFetcher_search_many
        assert len(result) > 0

    @my_vcr.use_cassette(f"{fixture_base_path}/ArtistFetcher_fetch_one.yaml")
    def test_fetch_one(self, artist_fetcher: ArtistFetcher):
        """Assert that fetch_one() will return data of this song"""
        result = artist_fetcher.fetch_one("3CsPxFJGyNa9ep79CFWN77")
        assert result is not None

    @my_vcr.use_cassette(f"{fixture_base_path}/ArtistFetcher_fetch_many.yaml")
    def test_fetch_many(self, artist_fetcher: ArtistFetcher, ArtistFetcher_search_many):
        """Assert that fetch_many() will iterate through the search inputs correctly'
        and returns data"""
        result = artist_fetcher.fetch_many(ArtistFetcher_search_many)
        assert len(result) > 0