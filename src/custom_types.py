from pydantic import BaseModel
from typing import Optional

# MDS types

class MdsSong(BaseModel):
    """Class to represent songs extracted from the MDS dataset"""    
    id: str
    title: str
    release: Optional[str]
    genre: Optional[str]
    artist_id: str
    artist_name: str
    year: Optional[int]

class MdsArtist(BaseModel):
    """Class to represent artists extracted from the MDS dataset"""
    id: str
    name: str
    location: Optional[str]
    tags: Optional[list[str]]


# Spotify types

class SongSearchResult(BaseModel):
    """Class to represent the search results of spotify.SongFetcher.search_one()"""
    mds_song_id: str
    spotify_song_ids: list[str]

class SpotifySong(BaseModel):
    """Class to represent the song data fetched from Spotify"""
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
    """Class to represent the search results of spotify.ArtistFetcher.search_one()"""
    mds_artist_id: str
    spotify_artist_ids: list[str]


class SpotifyArtist(BaseModel):
    """Class to represent the artist data fetched from Spotify"""
    id: str
    name: str
    url: str
    total_followers: Optional[int]
    popularity: Optional[float]
    genres: Optional[list[str]]


# Integrated data types
class IngegratedSongMetadata(BaseModel):
    """Class to represent song data integrated between MDS and Spotify"""
    mds_song_id: str
    spotify_songs: list[SpotifySong]

class IntegratedArtistMetadata(BaseModel):
    """class to represent artist data integrated between MDS and Spotify"""
    mds_artist_id: str
    spotify_artists: list[SpotifyArtist]