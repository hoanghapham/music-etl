from configparser import ConfigParser
from pathlib import Path

from prefect import task

from src import etl_queries as etl 
from src.msd.custom_types import MsdSong, MsdArtist
from src.aws.redshift import RedshiftClient
from src.data_quality import DataQualityOperator

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
def refresh_staging_schema(redshift: RedshiftClient, logger):
    logger.info("Preparing staging schema...")
    redshift.execute_query(prep_schema.drop_schema_staging)
    redshift.execute_query(prep_schema.create_schema_staging.format(user=redshift_user))


@task
def copy_s3_to_staging(redshift, create_table_query, table_name, source_path, logger):
    logger.info("Creating staging.msd_songs table...")
    redshift.execute_query(create_table_query)
    redshift.execute_query(loading.copy_s3_to_redshift.format(
        table           = table_name,
        iam_role        = iam_role,
        source_path     = source_path,
        region_name     = region_name
        )
    )


@task 
def search_spotify(redshift, spotify_fetcher, object_name, items_num=10, output_path="./", logger = None):
    logger.info(f"Searching for {object_name} on Spotify...")

    if object_name == 'songs':
        songs = redshift.execute_query(search.songs.format(items_num))
        search_inputs = [
            MsdSong(id=song[0], name=song[1], artist_id=song[2], artist_name=song[3]) 
            for song in songs
        ]
    
    elif object_name == 'artists':
        artists = redshift.execute_query(search.artists.format(items_num))
        search_inputs = [
            MsdArtist(id=artist[0], name=artist[1]) 
            for artist in artists
        ]

    search_results = spotify_fetcher.search_many(search_inputs)
    spotify_fetcher.output_json(search_results, output_path, new_line_delimited=True)
    
    return search_results
        

@task
def upload_files(s3, local_file_path, remote_file_path, logger):
    logger.info(f"Uploading to S3: {local_file_path}")
    s3.upload_file(local_file_path, bucket, remote_file_path)



@task
def fetch_spotify(spotify_search_results, spotify_fetcher, object_name, output_path, logger):
    logger.info(f"Fetching {object_name} from spotify...")

    fetch_result = spotify_fetcher.fetch_many(spotify_search_results)
    spotify_fetcher.output_json(fetch_result, output_path, new_line_delimited=True)


# Analytics tables

@task
def create_msd_tables(redshift, logger):
    redshift.execute_query(prep_schema.drop_schema_msd)
    redshift.execute_query(prep_schema.create_schema_msd.format(user=redshift_user))
    
    logger.info("Creating msd.songs table...")
    redshift.execute_query(analytics.create_table_msd_songs)
    
    logger.info("Creating msd.artists table...")
    redshift.execute_query(analytics.create_table_msd_artists)

@task
def create_spotify_tables(redshift, logger):
    redshift.execute_query(prep_schema.drop_schema_spotify)
    redshift.execute_query(prep_schema.create_schema_spotify.format(user=redshift_user))
    
    logger.info("Creating spotify.songs table...")
    redshift.execute_query(analytics.create_table_spotify_songs)
    
    logger.info("Creating spotify.artists table...")
    redshift.execute_query(analytics.create_table_spotify_artists)


@task
def create_mapped_tables(redshift, logger):
    redshift.execute_query(prep_schema.drop_schema_mapped)
    redshift.execute_query(prep_schema.create_schema_mapped.format(user=redshift_user))

    logger.info("Creating mapped.songs table...")
    redshift.execute_query(analytics.create_table_mapped_songs)

    logger.info("Creating mapped.songs table...")
    redshift.execute_query(analytics.create_table_mapped_artists)


@task
def create_analytics_tables(redshift, logger):
    redshift.execute_query(prep_schema.drop_schema_analytics)
    redshift.execute_query(prep_schema.create_schema_analytics.format(user=redshift_user))

    logger.info("Creating analytics.songs table...")
    redshift.execute_query(analytics.create_table_analytics_songs)
    
    logger.info("Creating analytics.songs table...")
    redshift.execute_query(analytics.create_table_analytics_artists)


@task
def run_data_quality_tests(redshift, tests, logger):
    data_quality = DataQualityOperator(client=redshift, logger=logger)
    data_quality.run_multi_tests(tests)