from pydantic import BaseModel
from src.spotify.custom_types import SpotifySong, SpotifyArtist

# Integrated data types
class IngegratedSongMetadata(BaseModel):
    """Class to represent song data integrated between MSD and Spotify"""
    msd_song_id: str
    spotify_songs: list[SpotifySong]

class IntegratedArtistMetadata(BaseModel):
    """class to represent artist data integrated between MSD and Spotify"""
    msd_artist_id: str
    spotify_artists: list[SpotifyArtist]