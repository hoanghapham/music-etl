from pydantic import BaseModel

class Test(BaseModel):
    name: str
    query: str
    expected_result: int

def has_data_query(table):
    return f"select count(*) as cnt from {table} having cnt = 0"

def unique_query(table, column):
    return f"select {column}, count(*) as cnt from {table} group by 1 having cnt > 1"

def not_null_query(table, column):
    return f"select count(*) as cnt from {table} where {column} is null"


all_tests = [
    
    # Test staging tables have data
    Test(name='staging_msd_songs_has_data', query = has_data_query('staging.msd_songs'), expected_result = 0),
    Test(name='staging_msd_artists_has_data', query = has_data_query('staging.msd_artists'), expected_result = 0),
    Test(name='staging_mapped_songs_has_data', query = has_data_query('staging.mapped_songs'), expected_result = 0),
    Test(name='staging_mapped_artists_has_data', query = has_data_query('staging.mapped_artists'), expected_result = 0),
    Test(name='staging_spotify_songs_has_data', query = has_data_query('staging.spotify_songs'), expected_result = 0),
    Test(name='staging_spotify_artists_has_data', query = has_data_query('staging.spotify_artists'), expected_result = 0),

    # Test analytics tables have data
    Test(name='analytics_songs_has_data', query = has_data_query('analytics.songs'), expected_result = 0),
    Test(name='analytics_artists_has_data', query = has_data_query('analytics.artists'), expected_result = 0),
    Test(name='msd_songs_has_data', query = has_data_query('msd.songs'), expected_result = 0),
    Test(name='msd_artists_has_data', query = has_data_query('msd.artists'), expected_result = 0),
    Test(name='mapped_songs_has_data', query = has_data_query('mapped.songs'), expected_result = 0),
    Test(name='mapped_artists_has_data', query = has_data_query('mapped.artists'), expected_result = 0),
    Test(name='spotify_songs_has_data', query = has_data_query('spotify.songs'), expected_result = 0),
    Test(name='spotify_artists_has_data', query = has_data_query('spotify.artists'), expected_result = 0),
    

    Test(name='msd_songs_id_unique', query = unique_query('msd.songs', 'id'), expected_result = 0),
    Test(name='msd_artists_id_unique', query = unique_query('msd.artists', 'id'), expected_result = 0),
    Test(name='mapped_songs_msd_song_id_unique', query = unique_query('mapped.songs', 'msd_song_id'), expected_result = 0),
    Test(name='mapped_artists_msd_artist_id_unique', query = unique_query('mapped.artists', 'msd_artist_id'), expected_result = 0),
    Test(name='spotify_songs_id_unique', query = unique_query('spotify.songs', 'id'), expected_result = 0),
    Test(name='spotify_artists_id_unique', query = unique_query('spotify.artists', 'id'), expected_result = 0),
    Test(name='analytics_spotify_songs_id_unique', query = unique_query('analytics.songs', 'spotify_song_id'), expected_result = 0),
    Test(name='analytics_spotify_songs_id_not_null', query = not_null_query('analytics.songs', 'spotify_song_id'), expected_result = 0),

]