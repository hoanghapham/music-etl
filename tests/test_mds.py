#%%
from pytest import fixture
from src.mds import SongsExtractor, ArtistsExtractor
import json

@fixture
def songs_extractor():
    songs_extractor = SongsExtractor()
    return songs_extractor

@fixture
def artists_extractor():
    artists_extractor = ArtistsExtractor()
    return artists_extractor

base_path = "tests/fixtures/mds"

class TestSongsExtractor():

    def test_extract_one(self, songs_extractor: SongsExtractor):
        song_01 = songs_extractor.extract_one(f"{base_path}/input/song_01.h5")

        with open(f"{base_path}/output/song_01.json", 'r') as f:
            output_song_01 = json.load(f)

        assert song_01 == output_song_01

    def test_extract_many(self, songs_extractor: SongsExtractor):
        songs = songs_extractor.extract_many(f"{base_path}/input/*.h5")

        with open(f"{base_path}/output/songs.json", 'r') as f:
            output_songs = json.load(f)

        assert all([i in output_songs for i in songs])


class TestArtistsExtractor():
    def test_extract_one(self, artists_extractor: ArtistsExtractor):
        artist_01 = artists_extractor.extract_one(f"{base_path}/input/song_01.h5")

        with open(f"{base_path}/output/artist_01.json", 'r') as f:
            output_artist_01 = json.load(f)

        assert artist_01 == output_artist_01

    def test_extract_many(self, artists_extractor: ArtistsExtractor):
        artists = artists_extractor.extract_many(f"{base_path}/input/*.h5")

        with open(f"{base_path}/output/artists.json", 'r') as f:
            output_artists = json.load(f)
        
        assert all([i in output_artists for i in artists])

