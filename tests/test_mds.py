#%%
from pytest import fixture
from src.mds import SongsExtractor

@fixture
def songs_extractor():
    songs_extractor = SongsExtractor()
    return songs_extractor

class TestSongsExtractor():

    def test_extract_one(self, songs_extractor):
        song_01 = songs_extractor.extract_one("tests/fixtures/mds/input/song_01.h5")

        output_song_01 = {
            'id': 'SOCIWDW12A8C13D406',
            'title': 'Soul Deep',
            'release': 'Dimensions',
            'genre': '',
            'artist_id': 'ARMJAGH1187FB546F3',
            'year': 1969
        }

        assert song_01 == output_song_01

    def test_extract_many(self, songs_extractor):
        songs = songs_extractor.extract_many("tests/fixtures/mds/input/*.h5")
        output_songs = [
            {
                'id': 'SOCIWDW12A8C13D406',
                'title': 'Soul Deep',
                'release': 'Dimensions',
                'genre': '',
                'artist_id': 'ARMJAGH1187FB546F3',
                'year': 1969
            },
            {
                'id': 'SONHOTT12A8C13493C',
                'title': 'Something Girls',
                'release': 'Friend Or Foe',
                'genre': '',
                'artist_id': 'AR7G5I41187FB4CE6C',
                'year': 1982
            }
        ]
        assert all([i in output_songs for i in songs])


