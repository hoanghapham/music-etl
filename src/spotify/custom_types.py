from pydantic import BaseModel
from typing import Optional

# Spotify types

class SongSearchResult(BaseModel):
    """Class to represent the search results of spotify.SongFetcher.search_one()"""
    msd_song_id: str
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
    msd_artist_id: str
    spotify_artist_ids: list[str]


class SpotifyArtist(BaseModel):
    """Class to represent the artist data fetched from Spotify"""
    id: str
    name: str
    url: str
    total_followers: Optional[int]
    popularity: Optional[float]
    genres: Optional[list[str]]
