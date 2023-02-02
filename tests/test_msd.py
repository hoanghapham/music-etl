from pytest import fixture
from src.msd import SongExtractor, ArtistExtractor
from src.msd.custom_types import MsdSong, MsdArtist
import json

@fixture
def song_extractor():
    song_extractor = SongExtractor()
    return song_extractor

@fixture
def artist_extractor():
    artist_extractor = ArtistExtractor()
    return artist_extractor

base_path = "tests/fixtures/msd"

class TestSongExtractor():

    def test_extract_one_file(self, song_extractor: SongExtractor):
        song_01 = song_extractor.extract_one_file(f"{base_path}/input/song_01.h5")[0]

        with open(f"{base_path}/output/song_01.json", 'r') as f:
            data = json.load(f)

        output_song_01 = MsdSong(**data)
        assert song_01 == output_song_01

    def test_extract_many_files(self, song_extractor: SongExtractor):
        songs = song_extractor.extract_many_files(f"{base_path}/input/*.h5")

        with open(f"{base_path}/output/songs.json", 'r') as f:
            data_json = json.load(f)

        output_songs = [MsdSong(**data) for data in data_json]
        assert all([i in output_songs for i in songs])


class TestArtistExtractor():
    def test_extract_one_file(self, artist_extractor: ArtistExtractor):
        artist_01 = artist_extractor.extract_one_file(f"{base_path}/input/song_01.h5")[0]

        with open(f"{base_path}/output/artist_01.json", 'r') as f:
            data = json.load(f)
        
        output_artist_01 = MsdArtist(**data)
        assert artist_01 == output_artist_01

    def test_extract_many_files(self, artist_extractor: ArtistExtractor):
        artists = artist_extractor.extract_many_files(f"{base_path}/input/*.h5")

        with open(f"{base_path}/output/artists.json", 'r') as f:
            data_json = json.load(f)
        
        output_artists = [MsdArtist(**data) for data in data_json]
        assert all([i in output_artists for i in artists])

