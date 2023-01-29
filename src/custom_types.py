from pydantic import BaseModel

# MDS types
class MdsSong(BaseModel):
    id: str
    title: str
    release: str
    genre: str
    artist_id: str
    artist_name: str
    year: int

class MdsArtist(BaseModel):
    id: str
    name: str
    location: str
    tags: list[str]

# Spotify types

class SongSearchResult(BaseModel):
    mds_song_id: str
    spotify_song_ids: list[str]

class SpotifySong(BaseModel):
    id: str
    name: str
    url: str
    external_ids: dict
    popularity: float
    available_markets: list[str]
    album: str
    artists: list[dict]
    duration_ms: int


class ArtistSearchResult(BaseModel):
    mds_artist_id: str
    spotify_artist_ids: list[str]


class SpotifyArtist(BaseModel):
    id: str
    name: str
    url: str
    total_followers: int
    popularity: float
    genres: list[str]


# Integrated data types
class IngegratedSongMetadata(BaseModel):
    mds_song_id: str
    spotify_songs: list[SpotifySong]

class IntegratedArtistMetadata(BaseModel):
    mds_artist_id: str
    spotify_artists: list[SpotifyArtist]