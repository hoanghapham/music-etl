import string
from configparser import ConfigParser
from pathlib import Path
from argparse import ArgumentParser

from src.msd import SongExtractor, ArtistExtractor
from src.aws.s3 import S3Client
from src.utils.custom_logger import init_logger


def main(search_dirs="A"):
    """Go through the song directories, extract H5 files for data and upload to S3.
    

    Parameters
    ----------
    search_dirs : str, optional
        The search_dirs argument is actually a string of capitalized characters, 
        for example "ABC". Default to "A"
    """    

    # Set up
    p = Path(__file__).with_name('config.cfg')
    config = ConfigParser()
    config.read(p)

    bucket = config['S3']['BUCKET']
    data_dir = config['DATA']['DATA_DIR']
    input_dir = config['DATA']['MSD_INPUT_DIR']
    output_dir = f"{data_dir}/msd/"

    logger = init_logger(Path(__file__).name)

    # Prepare client
    client = S3Client(
        region_name='us-west-2', 
        aws_access_key_id=config['AWS']['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['AWS']['AWS_SECRET_ACCESS_KEY'],
        aws_session_token=config['AWS']['AWS_SESSION_TOKEN'],
    )


    song_extractor = SongExtractor()
    artists_extractor = ArtistExtractor()

    patterns = []

    # Generate search pattern by appending two characters
    for char1 in search_dirs:
        for char2 in string.ascii_uppercase:
            patterns.append(f"{char1}/{char2}")

    
    # Walk through the search patterns, search for H5 files, 
    # and combine their data into a single JSON file.

    for pattern in patterns:
        search_path         = f"{input_dir}/{pattern}/**/*.h5"
        songs_output_dir   = f"{output_dir}/songs/{pattern}.json"
        artists_output_dir = f"{output_dir}/artists/{pattern}.json"
        songs_remote_path   = f"msd/songs/{pattern}.json"
        artists_remote_path = f"msd/artists/{pattern}.json"

        logger.info(f"Processing {search_path}")

        songs = song_extractor.extract_many_files(search_path)
        artists = artists_extractor.extract_many_files(search_path)

        if songs == []:
            continue
        else:
            song_extractor.output_json(songs, songs_output_dir)
            client.upload_file(songs_output_dir, bucket, songs_remote_path)

            artists_extractor.output_json(artists, artists_output_dir)
            client.upload_file(artists_output_dir, bucket, artists_remote_path)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-s", "--search_dirs", default="A")
    parser.add_argument('-m', '--mode', default='dev', choices=['dev', 'prod'], required=True)

    args = parser.parse_args()

    if args.mode == 'dev':
        # If run in dev mode, use search_dirs
        main(args.search_dirs)
    
    elif args.mode == 'prod':
        # If run in prod mode, go through all folders
        main(string.ascii_uppercase)