#%%
from configparser import ConfigParser
from pathlib import Path

from prefect import task, flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner

from src import etl_queries as etl 
from src.spotify import SpotifyClient, SongFetcher, ArtistFetcher
from src.msd.custom_types import MsdSong, MsdArtist
from src.aws.redshift import RedshiftClient
from src.aws.s3 import S3Client
from src.data_quality import DataQualityOperator, all_tests



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

    bucket              = config['S3']['BUCKET']
    msd_songs_path      = config['S3']['MSD_SONGS_PATH']
    msd_artists_path    = config['S3']['MSD_ARTISTS_PATH']
    region_name         = config['S3']['REGION_NAME']
    iam_role            = config['IAM']['IAM_ROLE_ARN']
    redshift_user       = config['REDSHIFT']['USERNAME']

    prep_schema     = etl.SchemaQueries()
    loading         = etl.LoadingQueries()
    stg_msd         = etl.StagingMsdQueries()
    stg_spotify     = etl.StagingSpotifyQueries()
    stg_mapped      = etl.StagingMappedQueries()
    analytics       = etl.AnalyticsQueries()
    #%%

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


    #%%

    # Prepare schemas
    @task
    def preppare_staging_schema():
        logger.info("Preparing staging schema...")
        redshift.execute_query(prep_schema.drop_schema_staging)
        redshift.execute_query(prep_schema.create_schema_staging.format(user=redshift_user))

    @task
    def stage_msd_tables():
        logger.info("Creating staging.msd_songs table...")
        redshift.execute_query(stg_msd.create_table_songs)
        redshift.execute_query(loading.copy_s3_to_redshift.format(
            table           = 'staging.msd_songs',
            iam_role        = iam_role,
            source_path     = msd_songs_path,
            region_name     = region_name
            )
        )

        logger.info("Creating staging.msd_artists table...")
        redshift.execute_query(stg_msd.create_table_artists)
        redshift.execute_query(loading.copy_s3_to_redshift.format(
            table           = 'staging.msd_artists',
            iam_role        = iam_role,
            source_path     = msd_artists_path,
            region_name     = region_name
            )
        )

    # %%
    #%%
    # Search

    @task
    def map_songs():
        limit = 10
        logger.info("Searching for songs on Spotify...")
        songs = redshift.execute_query(
            f"select id, name, artist_id, artist_name from staging.msd_songs limit {limit}")
        
        song_search_inputs = [
            MsdSong(id=song[0], name=song[1], artist_id=song[2], artist_name=song[3]) 
            for song in songs
        ]
        song_search_results = songs_fetcher.search_many(song_search_inputs)
        songs_fetcher.output_json(song_search_results, "data/mapped/songs.json", new_line_delimited=True)
        return song_search_results
        

    @task
    def upload_mapped_songs():
        logger.info("Uploading mapped songs to S3...")
        s3.upload_file("data/mapped/songs.json", bucket, "mapped/songs.json")


    @task
    def map_artists():
        limit = 10
        logger.info("Searching for artists on Spotify...")
        artists = redshift.execute_query(
            f"select distinct id, name from staging.msd_artists limit {limit}")
        
        artist_search_inputs = [
            MsdArtist(id=artist[0], name=artist[1]) 
            for artist in artists
        ]
        artist_search_results = artists_fetcher.search_many(artist_search_inputs)
        artists_fetcher.output_json(artist_search_results, "data/mapped/artists.json", new_line_delimited=True)
        return artist_search_results

    @task
    def upload_mapped_artists():
        logger.info("Uploading mapped artists to S3...")
        s3.upload_file("data/mapped/artists.json", bucket, "mapped/artists.json")


    @task
    def stage_mapped_tables():
        logger.info("Creating staging.mapped_songs table...")
        redshift.execute_query(stg_mapped.create_table_mapped_songs)
        redshift.execute_query(loading.copy_s3_to_redshift.format(
            table           = 'staging.mapped_songs',
            iam_role        = iam_role,
            source_path     = f"s3://{bucket}/mapped/songs.json",
            region_name     = region_name    
        ))

        logger.info("Creating staging.mapped_artists table...")
        redshift.execute_query(stg_mapped.create_table_mapped_artists)
        redshift.execute_query(loading.copy_s3_to_redshift.format(
            table           = 'staging.mapped_artists',
            iam_role        = iam_role,
            source_path     = f"s3://{bucket}/mapped/artists.json",
            region_name     = region_name    
        ))


    @task
    def fetch_spotify_songs(song_search_results):
        logger.info("Fetching songs from spotify...")
        spotify_songs = songs_fetcher.fetch_many(song_search_results)
        songs_fetcher.output_json(spotify_songs, "data/spotify/songs.json", new_line_delimited=True)
        return spotify_songs


    @task
    def fetch_spotify_artists(artist_search_results):
        logger.info("Fetching artists from Spotify...")
        spotify_artists = artists_fetcher.fetch_many(artist_search_results)
        artists_fetcher.output_json(spotify_artists, "data/spotify/artists.json", new_line_delimited=True)


    @task
    def upload_spotify_songs():
        logger.info("Uploading Spotify songs...")
        s3.upload_file("data/spotify/songs.json", bucket, "spotify/songs.json")

    @task
    def upload_spotify_artists():
        logger.info("Uploading Spotify artists...")
        s3.upload_file("data/spotify/artists.json", bucket, "spotify/artists.json")
    # %%

    # Stage spotify

    @task
    def stage_spotify_tables():
        logger.info("Creating staging.spotify_songs table...")
        redshift.execute_query(stg_spotify.create_table_songs)
        redshift.execute_query(loading.copy_s3_to_redshift.format(
            table           = 'staging.spotify_songs',
            iam_role        = iam_role,
            source_path     = f"s3://{bucket}/spotify/songs.json",
            region_name     = region_name
        ))

        logger.info("Creating staging.spotify_artists table...")
        redshift.execute_query(stg_spotify.create_table_artists)
        redshift.execute_query(loading.copy_s3_to_redshift.format(
            table           = 'staging.spotify_artists',
            iam_role        = iam_role,
            source_path     = f"s3://{bucket}/spotify/artists.json",
            region_name     = region_name
        ))

    @task
    def create_msd_tables():
        redshift.execute_query(prep_schema.drop_schema_msd)
        redshift.execute_query(prep_schema.create_schema_msd.format(user=redshift_user))
        
        logger.info("Creating msd.songs table...")
        redshift.execute_query(analytics.create_table_msd_songs)
        
        logger.info("Creating msd.artists table...")
        redshift.execute_query(analytics.create_table_msd_artists)

    @task
    def create_spotify_tables():
        redshift.execute_query(prep_schema.drop_schema_spotify)
        redshift.execute_query(prep_schema.create_schema_spotify.format(user=redshift_user))
        
        logger.info("Creating spotify.songs table...")
        redshift.execute_query(analytics.create_table_spotify_songs)
        
        logger.info("Creating spotify.artists table...")
        redshift.execute_query(analytics.create_table_spotify_artists)


    @task
    def create_mapped_tables():
        redshift.execute_query(prep_schema.drop_schema_mapped)
        redshift.execute_query(prep_schema.create_schema_mapped.format(user=redshift_user))

        logger.info("Creating mapped.songs table...")
        redshift.execute_query(analytics.create_table_mapped_songs)

        logger.info("Creating mapped.songs table...")
        redshift.execute_query(analytics.create_table_mapped_artists)


    @task
    def create_analytics_tables():
        redshift.execute_query(prep_schema.drop_schema_analytics)
        redshift.execute_query(prep_schema.create_schema_analytics.format(user=redshift_user))

        logger.info("Creating analytics.songs table...")
        redshift.execute_query(analytics.create_table_analytics_songs)
        
        logger.info("Creating analytics.songs table...")
        redshift.execute_query(analytics.create_table_analytics_artists)

    @task
    def run_data_quality_tests(test):
        data_quality = DataQualityOperator(client=redshift, logger=logger)
        data_quality.run_multi_tests(test)



# %%
    task_preppare_staging_schema        = preppare_staging_schema.submit()

    # Stage MSD tables
    task_stage_msd_tables               = stage_msd_tables.submit(wait_for=[task_preppare_staging_schema])

    # Map MSD and Spotify
    task_map_songs                      = map_songs.submit(wait_for=[task_stage_msd_tables])
    task_upload_mapped_songs            = upload_mapped_songs.submit(wait_for=[task_map_songs])
    
    task_map_artists                    = map_artists.submit(wait_for=[task_stage_msd_tables])
    task_upload_mapped_artists          = upload_mapped_artists.submit(wait_for=[task_map_artists])
    
    task_stage_mapped_tables            = stage_mapped_tables.submit(wait_for=[task_upload_mapped_songs, task_upload_mapped_artists])
    
    # Fetch Spotify
    task_fetch_spotify_songs            = fetch_spotify_songs.submit(task_map_songs)
    task_upload_spotify_songs           = upload_spotify_songs.submit(wait_for=[task_fetch_spotify_songs])
    
    task_fetch_spotify_artists          = fetch_spotify_artists.submit(task_map_artists)
    task_upload_spotify_artists         = upload_spotify_artists.submit(wait_for=[task_fetch_spotify_artists])
    
    task_stage_spotify_tables           = stage_spotify_tables.submit(wait_for=[task_upload_spotify_songs, task_upload_spotify_artists])

    # Create analytics tables

    task_create_msd_tables              = create_msd_tables.submit(wait_for=[task_stage_msd_tables])
    task_create_spotify_tables          = create_spotify_tables.submit(wait_for=[task_stage_spotify_tables])
    task_create_mapped_tables           = create_mapped_tables.submit(wait_for=[task_stage_mapped_tables])

    task_create_analytics_tables        = create_analytics_tables.submit(wait_for=[task_create_msd_tables, task_create_spotify_tables, task_create_mapped_tables])


    run_data_quality_tests.submit(all_tests, wait_for=[task_create_analytics_tables])

if __name__ == "__main__":
    music_etl()