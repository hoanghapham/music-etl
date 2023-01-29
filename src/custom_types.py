from pydantic import BaseModel
from typing import Optional

# MDS types
class MdsSong(BaseModel):
    id: str
    title: str
    release: Optional[str]
    genre: Optional[str]
    artist_id: str
    artist_name: str
    year: Optional[int]

class MdsArtist(BaseModel):
    id: str
    name: str
    location: Optional[str]
    tags: Optional[list[str]]

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
    album: Optional[str]
    artists: list[dict]
    duration_ms: int


class ArtistSearchResult(BaseModel):
    mds_artist_id: str
    spotify_artist_ids: list[str]


class SpotifyArtist(BaseModel):
    id: str
    name: str
    url: str
    total_followers: Optional[int]
    popularity: Optional[float]
    genres: Optional[list[str]]


# Integrated data types
class IngegratedSongMetadata(BaseModel):
    mds_song_id: str
    spotify_songs: list[SpotifySong]

class IntegratedArtistMetadata(BaseModel):
    mds_artist_id: str
    spotify_artists: list[SpotifyArtist]