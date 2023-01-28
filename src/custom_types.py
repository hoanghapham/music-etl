from pydantic import BaseModel

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