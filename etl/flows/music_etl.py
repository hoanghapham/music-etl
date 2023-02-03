from configparser import ConfigParser
from pathlib import Path

from prefect import flow, get_run_logger
from prefect.task_runners import SequentialTaskRunner

from src import etl_queries as queries
from src.aws.s3 import S3Client
from src.aws.redshift import RedshiftClient
from src.spotify import SpotifyClient, SongFetcher, ArtistFetcher
from src.data_quality import all_tests

from flows import common_tasks as etl

@flow(
    task_runner=SequentialTaskRunner(),
    name='music_etl', 
    description="""
        Load source msd data from S3, search for songs and artists in Spotify, and then combine in final analytics tables.
    """
    )
def music_etl():

    logger = get_run_logger()

    p = Path(__file__).with_name('config.cfg')
    config = ConfigParser()
    config.read(p)

    region_name         = config['S3']['REGION_NAME']
    data_dir            = config['DATA']['DATA_DIR']

    s3_msd_songs        = config['S3']['S3_MSD_SONGS']
    s3_msd_artists      = config['S3']['S3_MSD_ARTISTS']
    s3_spotify_songs    = config['S3']['S3_SPOTIFY_SONGS']
    s3_spotify_artists  = config['S3']['S3_SPOTIFY_ARTISTS']
    s3_mapped_songs     = config['S3']['S3_MAPPED_SONGS']
    s3_mapped_artists   = config['S3']['S3_MAPPED_ARTISTS']

    stg_msd         = queries.StagingMsdQueries()
    stg_spotify     = queries.StagingSpotifyQueries()
    stg_mapped      = queries.StagingMappedQueries()

    redshift = RedshiftClient(
        host        = config['REDSHIFT']['HOST'],
        port        = int(config['REDSHIFT']['PORT']),
        database    = config['REDSHIFT']['DATABASE'],
        user        = config['REDSHIFT']['USERNAME'],
        password    = config['REDSHIFT']['PASSWORD'],
        logger      = logger
    )

    s3 = S3Client(
        region_name             = region_name,
        aws_access_key_id       = config['AWS']['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key   = config['AWS']['AWS_SECRET_ACCESS_KEY'],
        aws_session_token       = config['AWS']['AWS_SESSION_TOKEN'],
        logger                  = logger
    )

    spotify = SpotifyClient(
        client_id       = config['SPOTIFY']['CLIENT_ID'], 
        client_secret   = config['SPOTIFY']['CLIENT_SECRET'],
        logger          = logger
    )
    
    artists_fetcher = ArtistFetcher(spotify, logger)
    songs_fetcher = SongFetcher(spotify, logger)


    refresh_staging_schema  = etl.refresh_staging_schema.submit(redshift, logger)

    # create staging MSD tables
    stage_msd_songs     = etl.copy_s3_to_staging.submit(redshift, stg_msd.create_table_songs, 'staging.msd_songs', s3_msd_songs, 
                                                logger, wait_for = [refresh_staging_schema])

    stage_msd_artists   = etl.copy_s3_to_staging.submit(redshift, stg_msd.create_table_artists, 'staging.msd_artists', s3_msd_artists, 
                                                logger, wait_for = [refresh_staging_schema])


    # Search MSD songs on spotify & create staging tables
    mapped_songs        = etl.search_spotify.submit(redshift, songs_fetcher, 'songs', 20, f"{data_dir}/mapped/songs.json", 
                                                logger, wait_for = [stage_msd_songs])
    
    mapped_artists      = etl.search_spotify.submit(redshift, artists_fetcher, 'artists', 20, f"{data_dir}/mapped/artists.json", 
                                                logger, wait_for = [stage_msd_artists])


    upload_mapped_songs     = etl.upload_files.submit(s3, f"{data_dir}/mapped/songs.json", "mapped/songs.json", logger, wait_for = [mapped_songs])
    upload_mapped_artists   = etl.upload_files.submit(s3, f"{data_dir}/mapped/artists.json","mapped/artists.json", logger, wait_for = [mapped_artists])


    stage_mapped_songs      = etl.copy_s3_to_staging.submit(redshift, stg_mapped.create_table_songs,'staging.mapped_songs', s3_mapped_songs, 
                                                logger, wait_for = [upload_mapped_songs])

    stage_mapped_artists    = etl.copy_s3_to_staging.submit(redshift, stg_mapped.create_table_artists,'staging.mapped_artists', s3_mapped_artists, 
                                                logger, wait_for = [upload_mapped_artists])

    
    # Use search result to fetch details from Spotify
    fetch_spotify_songs     = etl.fetch_spotify.submit(mapped_songs, songs_fetcher, 'songs', f"{data_dir}/spotify/songs.json", logger)
    fetch_spotify_artists   = etl.fetch_spotify.submit(mapped_artists, artists_fetcher, 'artists', f"{data_dir}/spotify/artists.json", logger)
    
    upload_spotify_songs    = etl.upload_files.submit(s3, f"{data_dir}/spotify/songs.json", "spotify/songs.json", logger, wait_for = [fetch_spotify_songs])
    upload_spotify_artists  = etl.upload_files.submit(s3, f"{data_dir}/spotify/artists.json", "spotify/artists.json", logger, wait_for = [fetch_spotify_artists])

    stage_spotify_songs     = etl.copy_s3_to_staging.submit(redshift, stg_spotify.create_table_songs, "staging.spotify_songs", s3_spotify_songs, 
                                                        logger, wait_for = [upload_spotify_songs])

    stage_spotify_artists   = etl.copy_s3_to_staging.submit(redshift, stg_spotify.create_table_artists, "staging.spotify_artists", s3_spotify_artists, 
                                                        logger, wait_for = [upload_spotify_artists])
    
    
    # Create analytics tables

    create_msd_tables              = etl.create_msd_tables.submit(redshift, logger, wait_for=[stage_msd_songs, stage_msd_artists])
    create_spotify_tables          = etl.create_spotify_tables.submit(redshift, logger, wait_for=[stage_spotify_songs, stage_spotify_artists])
    create_mapped_tables           = etl.create_mapped_tables.submit(redshift, logger, wait_for=[stage_mapped_songs, stage_mapped_artists])

    create_analytics_tables        = etl.create_analytics_tables.submit(redshift, logger, 
                                        wait_for=[
                                            create_msd_tables, 
                                            create_spotify_tables, 
                                            create_mapped_tables
                                        ])


    etl.run_data_quality_tests.submit(redshift, all_tests, logger, wait_for=[create_analytics_tables])

if __name__ == "__main__":
    music_etl()