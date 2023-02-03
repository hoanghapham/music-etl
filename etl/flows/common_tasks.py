from configparser import ConfigParser
from pathlib import Path
from logging import Logger
from prefect import task

from src import etl_queries as etl 
from src.msd.custom_types import MsdSong, MsdArtist
from src.spotify import SongFetcher, ArtistFetcher
from src.spotify.custom_types import SpotifyArtist, SpotifySong
from src.mapping.custom_types import MappedArtist, MappedSong
from src.aws.redshift import RedshiftClient
from src.aws.s3 import S3Client
from src.data_quality import DataQualityOperator
from src.data_quality.tests import Test


prep_schema     = etl.SchemaQueries()
loading         = etl.LoadingQueries()
stg_msd         = etl.StagingMsdQueries()
stg_spotify     = etl.StagingSpotifyQueries()
stg_mapped      = etl.StagingMappedQueries()
analytics       = etl.AnalyticsQueries()
search          = etl.SearchInputQueries()

p = Path(__file__).with_name('config.cfg')
config = ConfigParser()
config.read(p)

bucket              = config['S3']['BUCKET']
redshift_user       = config['REDSHIFT']['USERNAME']
region_name         = config['S3']['REGION_NAME']
iam_role            = config['IAM']['IAM_ROLE_ARN']
data_dir            = config['DATA']['DATA_DIR']

@task
def refresh_staging_schema(redshift: RedshiftClient, logger: Logger):
    """Task to drop and then recreate the staging schema

    Parameters
    ----------
    redshift : RedshiftClient
        A RedshiftClient object
    logger : Logger
    """
    logger.info("Preparing staging schema...")
    redshift.execute_query(prep_schema.drop_schema_staging)
    redshift.execute_query(prep_schema.create_schema_staging.format(user=redshift_user))


@task
def copy_s3_to_staging(
        redshift: RedshiftClient, 
        create_table_query: str, 
        table_name: str, 
        source_path: str, 
        logger: Logger
    ):
    """Task to copy data from the staging tables

    Parameters
    ----------
    redshift : RedshiftClient
    create_table_query : str
        A query to create the staging table
    table_name : str
        Name of the table being created, for logging purpose
    source_path : str
        Path to the S3 object to be loaded to redshift
    logger : Logger
    """

    logger.info(f"Creating {table_name} table...")
    redshift.execute_query(create_table_query)
    redshift.execute_query(loading.copy_s3_to_redshift.format(
        table           = table_name,
        iam_role        = iam_role,
        source_path     = source_path,
        region_name     = region_name
        )
    )


@task 
def search_spotify(
        redshift: RedshiftClient, 
        spotify_fetcher: SongFetcher | ArtistFetcher, 
        object_name: str, 
        limit_clause: str ="limit 10", 
        output_path: str = "./tmp", 
        logger: Logger = None
    ) -> list[MappedSong | MappedArtist]:
    """Query songs / artists info from the staging tables, and search for those 
    songs / artists on Spotify.

    Parameters
    ----------
    redshift : RedshiftClient
        Redshift client used to query songs/artists from staging table 
        and use as search input
    spotify_fetcher : SongFetcher | ArtistFetcher
        One of the two fetchers to fetch either songs or artists
    object_name : str
        Name of the object being searched, for logging & branching purpos
    limit_clause : str, optional
        the LIMIT clause to be inserted to the search query, by default "limit 10"
    output_path : str, optional
        Local folder to write searched data to, by default "./tmp"
    logger : Logger

    TODO: Should do branching using the fetcher's type instead of string like this?
    TODO: Find a better way to generate search queries with LIMIT
    
    Returns
    -------
    list[MappedSong | MappedArtist]
        List of MappedSong or MappedArtist objects
    """
    logger.info(f"Searching for {object_name} on Spotify...")

    if object_name == 'songs':
        songs = redshift.execute_query(search.songs.format(limit_clause=limit_clause))
        search_inputs = [
            MsdSong(id=song[0], name=song[1], artist_id=song[2], artist_name=song[3]) 
            for song in songs
        ]
    
    elif object_name == 'artists':
        artists = redshift.execute_query(search.artists.format(limit_clause=limit_clause))
        search_inputs = [
            MsdArtist(id=artist[0], name=artist[1]) 
            for artist in artists
        ]

    search_results = spotify_fetcher.search_many(search_inputs)
    spotify_fetcher.output_json(search_results, output_path, new_line_delimited=True)
    
    return search_results
        

@task
def upload_files(s3: S3Client, local_file_path: str, 
                remote_file_path: str, logger: Logger):
    """Task to upload local files to S3

    Parameters
    ----------
    s3 : S3Client
        S3 client to upload file
    local_file_path : str
        Path to the file in the local machine to be uploaded
    remote_file_path : str
        File path on S3 to upload the file to. No need to include the bucket name.
    logger : Logger
    """
    logger.info(f"Uploading to S3: {local_file_path}")
    s3.upload_file(local_file_path, bucket, remote_file_path)



@task
def fetch_spotify(
        spotify_search_results: list[SpotifySong | SpotifyArtist], 
        spotify_fetcher: SongFetcher | ArtistFetcher, 
        object_name: str, 
        output_path: str, 
        logger: Logger
    ):
    """Fetch songs/artists from spotify and output file to a local folder

    Parameters
    ----------
    spotify_search_results : list[SpotifySong  |  SpotifyArtist]
        Search result retuned by search_spotify() task
    spotify_fetcher : SongFetcher | ArtistFetcher
        Spotify fetcher to fetch songs/artists details
    object_name : str
        Name of the object to fetch
    output_path : str
        Local path to write the fetched results to
    logger : Logger
    """
    logger.info(f"Fetching {object_name} From spotify...")

    fetch_result = spotify_fetcher.fetch_many(spotify_search_results)
    spotify_fetcher.output_json(fetch_result, output_path, new_line_delimited=True)


# Analytics tables

@task
def create_msd_tables(redshift: RedshiftClient, logger: Logger):
    """Task to create cleaned songs & artists tables in the msd schema

    Parameters
    ----------
    redshift : RedshiftClient
        Redshift client to run queries
    logger : Logger
    """
    
    redshift.execute_query(prep_schema.drop_schema_msd)
    redshift.execute_query(prep_schema.create_schema_msd.format(user=redshift_user))
    
    logger.info("Creating msd.songs table...")
    redshift.execute_query(analytics.create_table_msd_songs)
    
    logger.info("Creating msd.artists table...")
    redshift.execute_query(analytics.create_table_msd_artists)

@task
def create_spotify_tables(redshift, logger):
    """Task to create cleaned songs & artists tables in the spotify schema

    Parameters
    ----------
    redshift : RedshiftClient
        Redshift client to run queries
    logger : Logger
    """
    redshift.execute_query(prep_schema.drop_schema_spotify)
    redshift.execute_query(prep_schema.create_schema_spotify.format(user=redshift_user))
    
    logger.info("Creating spotify.songs table...")
    redshift.execute_query(analytics.create_table_spotify_songs)
    
    logger.info("Creating spotify.artists table...")
    redshift.execute_query(analytics.create_table_spotify_artists)


@task
def create_mapped_tables(redshift, logger):
    """Task to create cleaned songs & artists tables in the mapped schema

    Parameters
    ----------
    redshift : RedshiftClient
        Redshift client to run queries
    logger : Logger
    """
    redshift.execute_query(prep_schema.drop_schema_mapped)
    redshift.execute_query(prep_schema.create_schema_mapped.format(user=redshift_user))

    logger.info("Creating mapped.songs table...")
    redshift.execute_query(analytics.create_table_mapped_songs)

    logger.info("Creating mapped.songs table...")
    redshift.execute_query(analytics.create_table_mapped_artists)


@task
def create_analytics_tables(redshift, logger):
    """Task to create cleaned songs & artists tables in the analytics schema

    Parameters
    ----------
    redshift : RedshiftClient
        Redshift client to run queries
    logger : Logger
    """
    redshift.execute_query(prep_schema.drop_schema_analytics)
    redshift.execute_query(prep_schema.create_schema_analytics.format(user=redshift_user))

    logger.info("Creating analytics.songs table...")
    redshift.execute_query(analytics.create_table_analytics_songs)
    
    logger.info("Creating analytics.songs table...")
    redshift.execute_query(analytics.create_table_analytics_artists)


@task
def run_data_quality_tests(redshift: RedshiftClient, tests: list[Test], logger: Logger):
    """Task to iterate through a list of data tests, run and report the results to

    Parameters
    ----------
    redshift : RedshiftClient
        Redshift client to run test queries
    tests : list[Test]
        List of Test objects to run
    logger : Logger
    """    
    data_quality = DataQualityOperator(client=redshift, logger=logger)
    data_quality.run_multi_tests(tests)