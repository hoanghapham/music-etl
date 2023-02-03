class LoadingQueries:

    copy_s3_to_redshift = """
    COPY {table}
    FROM '{source_path}'
    IAM_ROLE '{iam_role}'
    FORMAT AS JSON 'auto'
    REGION '{region_name}'
    """

    unload_redshift_to_s3 = ""

class SearchInputQueries:
    songs = "select id, name, artist_id, artist_name from staging.msd_songs limit {}"
    artists = "select distinct id, name from staging.msd_artists limit {}"

class SchemaQueries:

    drop_schema_msd         = "DROP SCHEMA IF EXISTS msd CASCADE"
    drop_schema_mapped      = "DROP SCHEMA IF EXISTS mapped CASCADE"
    drop_schema_spotify     = "DROP SCHEMA IF EXISTS spotify CASCADE"
    drop_schema_staging     = "DROP SCHEMA IF EXISTS staging CASCADE"
    drop_schema_analytics   = "DROP SCHEMA IF EXISTS analytics CASCADE"

    create_schema_msd       = "CREATE SCHEMA IF NOT EXISTS msd AUTHORIZATION {user}"
    create_schema_mapped    = "CREATE SCHEMA IF NOT EXISTS mapped AUTHORIZATION {user}"
    create_schema_spotify   = "CREATE SCHEMA IF NOT EXISTS spotify AUTHORIZATION {user}"
    create_schema_staging   = "CREATE SCHEMA IF NOT EXISTS staging AUTHORIZATION {user}"
    create_schema_analytics = "CREATE SCHEMA IF NOT EXISTS analytics AUTHORIZATION {user}"


class StagingMsdQueries:

    drop_table_artists      = "DROP TABLE IF EXISTS staging.msd_artists"
    drop_table_songs        = "DROP TABLE IF EXISTS staging.msd_songs"

    create_table_artists = """
    CREATE TABLE IF NOT EXISTS staging.msd_artists (
        id          VARCHAR(256) NOT NULL,
        name        VARCHAR(256),
        location    VARCHAR(256),
        longitude   NUMERIC,
        latitude    NUMERIC,
        tags        SUPER
    )
    DISTSTYLE KEY
    DISTKEY(id)
    """

    create_table_songs = """
    CREATE TABLE IF NOT EXISTS staging.msd_songs (
        id              VARCHAR(256) NOT NULL,
        name            VARCHAR(256),
        release         VARCHAR(256),
        genre           VARCHAR(256),
        artist_id       VARCHAR(256),
        artist_name     VARCHAR(256),
        year            INTEGER
    )
    DISTSTYLE KEY
    DISTKEY(id)
    """


class StagingMappedQueries:
    
    drop_table_songs     = "DROP TABLE IF EXISTS staging.mapped_songs"
    drop_table_artists   = "DROP TABLE IF EXISTS staging.mapped_artists"

    create_table_songs = """
    CREATE TABLE IF NOT EXISTS staging.mapped_songs (
        msd_song_id VARCHAR(256),
        spotify_song_ids SUPER
    )
    DISTSTYLE KEY
    DISTKEY(msd_song_id)
    """

    create_table_artists = """
    CREATE TABLE IF NOT EXISTS staging.mapped_artists (
        msd_artist_id VARCHAR(256),
        spotify_artist_ids SUPER
    )
    DISTSTYLE KEY
    DISTKEY(msd_artist_id)
    """


class StagingSpotifyQueries:
    
    drop_table_songs        = """DROP TABLE IF EXISTS staging.spotify_songs"""
    drop_table_artists      = """DROP TABLE IF EXISTS staging.spotify_artists"""

    create_table_songs = """
    CREATE TABLE IF NOT EXISTS staging.spotify_songs (
        id                  VARCHAR(256),
        name                VARCHAR(256),
        url                 VARCHAR(MAX),
        external_ids        SUPER,
        popularity          NUMERIC,
        available_markets   SUPER,
        album_id            VARCHAR(256),
        artists             SUPER,
        duration_ms         INTEGER
    )
    DISTSTYLE KEY
    DISTKEY(id)
    """

    create_table_artists = """
    CREATE TABLE IF NOT EXISTS staging.spotify_artists (
        id                  VARCHAR(256),
        name                VARCHAR(256),
        url                 VARCHAR(MAX),
        total_followers     INTEGER,
        popularity          NUMERIC,
        genres              SUPER
    )
    DISTSTYLE KEY
    DISTKEY(id)
    """


class AnalyticsQueries:

    drop_table_analytics_songs      = "DROP TABLE IF EXISTS analytics.songs"
    drop_table_analytics_artists    = "DROP TABLE IF EXISTS analytics.artists"

    drop_table_msd_songs            = "DROP TABLE IF EXISTS msd.songs"
    drop_table_msd_artists          = "DROP TABLE IF EXISTS msd.artists"

    drop_table_spotify_songs        = "DROP TABLE IF EXISTS spotify.songs"
    drop_table_spotify_artists      = "DROP TABLE IF EXISTS spotify.artists"

    drop_table_mapped_songs         = "DROP TABLE IF EXISTS mapped.songs"
    drop_table_mapped_artists       = "DROP TABLE IF EXISTS mapped.artists"

    create_table_msd_songs  = """
    CREATE TABLE msd.songs 
    DISTSTYLE KEY
    DISTKEY(id)
    AS 
    with base as (
        select 
            *
            , row_number() over (partition by id) as idx
        from staging.msd_songs
    )
    select
        id
        , name
        , release
        , genre
        , artist_id
        , artist_name
        , year
    from base
    where idx = 1
    """ 
    
    create_table_msd_artists = """
    CREATE TABLE msd.artists 
    DISTSTYLE KEY
    DISTKEY(id)
    AS 
    with base as (
        select 
            *
            , row_number() over (partition by id) as idx
        from staging.msd_artists
    )
    select
        id
        , name
        , location
        , longitude
        , latitude
        , tags
    from base
    where idx = 1
    """

    create_table_spotify_songs = """
    CREATE TABLE spotify.songs 
    DISTSTYLE KEY
    DISTKEY(id)
    AS 
    with base as (
        select 
            *
            , row_number() over (partition by id) as idx
        from staging.spotify_songs
    )
    select
        id
        , name
        , url
        , external_ids
        , popularity
        , available_markets
        , album_id
        , artists
        , duration_ms
    from base
    where idx = 1
    """

    create_table_spotify_artists = """
    CREATE TABLE spotify.artists 
    DISTSTYLE KEY
    DISTKEY(id)
    AS 
    with base as (
        select 
            *
            , row_number() over (partition by id) as idx
        from staging.spotify_artists
    )
    select
        id
        , name
        , url
        , total_followers
        , popularity
        , genres
    from base
    where idx = 1
    """

    create_table_mapped_songs = """
    CREATE TABLE mapped.songs 
    DISTSTYLE ALL
    AS
    with base as (
        select 
            *
            , row_number() over (partition by msd_song_id) as idx
        from staging.mapped_songs
    )
    select
        msd_song_id
        , spotify_song_ids
    from base
    where idx = 1
    """

    create_table_mapped_artists = """
    CREATE TABLE mapped.artists 
    DISTSTYLE ALL
    AS 
    with base as (
        select 
            *
            , row_number() over (partition by msd_artist_id) as idx
        from staging.mapped_artists
    )
    select
        msd_artist_id
        , spotify_artist_ids
    from base
    where idx = 1
    """


    create_table_analytics_songs = """
    CREATE TABLE analytics.songs AS
    WITH unnested AS (
        SELECT 
            msd_song_id,
            CAST(spotify_song_id AS VARCHAR) AS spotify_song_id
        FROM mapped.songs as mapped_songs
        , mapped_songs.spotify_song_ids AS spotify_song_id
    )

    SELECT 
        unnested.msd_song_id
        , msd.name              as msd_song_name
        , msd.release           as msd_release
        , msd.artist_name       as msd_artist_name
        , msd.genre
        , msd.year
        
        , unnested.spotify_song_id
        , spotify.name          as spotify_song_name
        , spotify.url           as spotify_url
        , spotify.popularity    as spotify_popularity
        , spotify.duration_ms
        , spotify.album_id

    FROM unnested
    LEFT JOIN msd.songs AS msd ON unnested.msd_song_id = msd.id
    LEFT JOIN spotify.songs AS spotify ON unnested.spotify_song_id = spotify.id
    WHERE spotify.id is not null
    """

    create_table_analytics_artists = """
    CREATE TABLE analytics.artists AS
    with unnested as (
        SELECT 
            msd_artist_id,
            CAST(spotify_artist_id AS VARCHAR) AS spotify_artist_id
        FROM mapped.artists as mapped_artists
        , mapped_artists.spotify_artist_ids as spotify_artist_id
    )
    SELECT
        unnested.msd_artist_id
        , msd.name                  as msd_artist_name
        , msd.location              as msd_location
        , msd.latitude              as msd_latitude
        , msd.longitude             as msd_longitude
        , msd.tags                  as msd_tags
        
        , unnested.spotify_artist_id
        , spotify.name              as spotify_artist_name
        , spotify.url               as spotify_artist_url
        , spotify.total_followers   as spotify_total_followers
        , spotify.genres            as spotify_genres

    FROM unnested
    LEFT JOIN msd.artists AS msd ON unnested.msd_artist_id = msd.id
    LEFT JOIN spotify.artists AS spotify ON unnested.spotify_artist_id = spotify.id
    WHERE spotify.id is not NULL
    """