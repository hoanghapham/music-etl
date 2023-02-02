from pydantic import BaseModel
from typing import Optional

class SpotifySong(BaseModel):
    """Class to represent the song data fetched from Spotify"""
    id                  : str
    name                : str
    url                 : str
    external_ids        : dict
    popularity          : float
    available_markets   : list[str]
    album_id            : Optional[str]
    artists             : list[dict]
    duration_ms         : int


class SpotifyArtist(BaseModel):
    """Class to represent the artist data fetched from Spotify"""
    id                  : str
    name                : str
    url                 : str
    total_followers     : Optional[int]
    popularity          : Optional[float]
    genres              : Optional[list[str]]
