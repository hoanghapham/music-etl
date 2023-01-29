from pytest import fixture
import vcr
import os
from src.spotify import ArtistFetcher, SongFetcher, SpotifyClient
from src.custom_types import MdsArtist, MdsSong
from dotenv import load_dotenv
from src.utils.custom_logger import init_logger


# Setup
load_dotenv()
my_vcr = vcr.VCR(filter_headers=['Authorization'])
fixture_base_path = 'tests/fixtures/vcr_cassettes/spotify'
logger = init_logger(__file__)


# Test SongFetcher ----------------------------------------

@fixture
def mds_song():
    return MdsSong(
        id='SOBBUGU12A8C13E95D',
        title='Setting Fire to Sleeping Giants',
        artist_id='ARMAC4T1187FB3FA4C',
        artist_name='The Dillinger Escape Plan'
    )

@fixture
def mds_songs():
    return [
        MdsSong(
            id='SOBBUGU12A8C13E95D',
            title='Setting Fire to Sleeping Giants',
            artist_id='ARMAC4T1187FB3FA4C',
            artist_name='The Dillinger Escape Plan'
        ),
        MdsSong(
            id='SOOGFBZ12AC3DF7FF2',
            title='In A Subtle Way',
            artist_id='ARDD1RC1187B9B52B4',
            artist_name='Jacob Young',
        )
    ]

@fixture(scope='module')
def client():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET') 
    return SpotifyClient(client_id, client_secret)

@fixture(scope='module')
def song_fetcher(client):
    song_fetcher = SongFetcher(client)
    return song_fetcher

@fixture
@my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_search_many.yaml")
def SongFetcher_search_many(song_fetcher: SongFetcher, mds_songs):
    result = song_fetcher.search_many(mds_songs)
    return result


class TestSongFetcher():

    @my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_search_one.yml")
    def test_search_one(self, song_fetcher: SongFetcher, mds_song):
        result = song_fetcher.search_one(mds_song)
        assert result is not None

    def test_search_many(self, SongFetcher_search_many):
        result = SongFetcher_search_many
        assert len(result) > 0

    @my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_fetch_one.yml")
    def test_fetch_one(self, song_fetcher: SongFetcher):
        result = song_fetcher.fetch_one("2ZyNYdziwt0ZS9mxRiwnXM")
        assert result is not None

    @my_vcr.use_cassette(f"{fixture_base_path}/SongFetcher_fetch_many.yml")
    def test_fetch_many(self, song_fetcher: SongFetcher, SongFetcher_search_many):
        result = song_fetcher.fetch_many(SongFetcher_search_many)
        assert len(result) > 0


# Test ArtistFetcher --------------------------------------------

@fixture
def artist_fetcher(client):
    return ArtistFetcher(client)

@fixture
def mds_artist():
    return MdsArtist(id='ARMJAGH1187FB546F3', name='The Box Tops')

@fixture
def mds_artists():
    return [
        MdsArtist(id='ARMJAGH1187FB546F3', name='The Box Tops'),
        MdsArtist(id='ARKRRTF1187B9984DA', name='Sonora Santanera')
    ]

@fixture
@my_vcr.use_cassette(f"{fixture_base_path}/ArtistFetcher_search_many.yaml")
def ArtistFetcher_search_many(artist_fetcher: ArtistFetcher, mds_artists):
    result = artist_fetcher.search_many(mds_artists)
    return result


class TestArtistFetcher():

    @my_vcr.use_cassette(f"{fixture_base_path}/ArtistFetcher_search_one.yaml")
    def test_search_one(self, artist_fetcher: ArtistFetcher, mds_artist):
        result = artist_fetcher.search_one(mds_artist)
        assert result is not None

    def test_search_many(self, ArtistFetcher_search_many):
        result = ArtistFetcher_search_many
        assert len(result) > 0

    def test_fetch_one(self, artist_fetcher: ArtistFetcher):
        result = artist_fetcher.fetch_one("3CsPxFJGyNa9ep79CFWN77")
        assert result is not None

    def test_fetch_many(self, artist_fetcher: ArtistFetcher, ArtistFetcher_search_many):
        result = artist_fetcher.fetch_many(ArtistFetcher_search_many)
        assert len(result) > 0