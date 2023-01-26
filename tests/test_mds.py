#%%
from pytest import fixture
from src.mds import SongExtractor, ArtistExtractor
import json

@fixture
def song_extractor():
    song_extractor = SongExtractor()
    return song_extractor

@fixture
def artist_extractor():
    artist_extractor = ArtistExtractor()
    return artist_extractor

base_path = "tests/fixtures/mds"

class TestSongExtractor():

    def test_extract_one(self, song_extractor: SongExtractor):
        song_01 = song_extractor.extract_one(f"{base_path}/input/song_01.h5")

        with open(f"{base_path}/output/song_01.json", 'r') as f:
            output_song_01 = json.load(f)

        assert song_01 == output_song_01

    def test_extract_many(self, song_extractor: SongExtractor):
        songs = song_extractor.extract_many(f"{base_path}/input/*.h5")

        with open(f"{base_path}/output/songs.json", 'r') as f:
            output_songs = json.load(f)

        assert all([i in output_songs for i in songs])


class TestArtistExtractor():
    def test_extract_one(self, artist_extractor: ArtistExtractor):
        artist_01 = artist_extractor.extract_one(f"{base_path}/input/song_01.h5")

        with open(f"{base_path}/output/artist_01.json", 'r') as f:
            output_artist_01 = json.load(f)

        assert artist_01 == output_artist_01

    def test_extract_many(self, artist_extractor: ArtistExtractor):
        artists = artist_extractor.extract_many(f"{base_path}/input/*.h5")

        with open(f"{base_path}/output/artists.json", 'r') as f:
            output_artists = json.load(f)
        
        assert all([i in output_artists for i in artists])

