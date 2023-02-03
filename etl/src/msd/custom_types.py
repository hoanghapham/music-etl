from pydantic import BaseModel
from typing import Optional

# MSD types

class MsdSong(BaseModel):
    """Class to represent songs extracted from the MSD dataset"""    
    id          : str
    name        : str
    release     : Optional[str]
    genre       : Optional[str]
    artist_id   : str
    artist_name : str
    year        : Optional[int]

class MsdArtist(BaseModel):
    """Class to represent artists extracted from the MSD dataset"""
    id          : str
    name        : str
    location    : Optional[str]
    latitude    : Optional[float]
    longitude   : Optional[float]
    tags        : Optional[list[str]]

