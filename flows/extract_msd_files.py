#%%
import string
from configparser import ConfigParser

from src.aws.s3 import S3Client
from src.msd import SongExtractor, ArtistExtractor
from src.utils.custom_logger import init_logger

# Set up
config = ConfigParser()
config.read("./config.cfg")

bucket = config['S3']['BUCKET']
data_path = "/media/hapham/data/projects/data/MillionSongSubset"
output_path = "data/msd"

logger = init_logger(__name__)

# Prepare client
client = S3Client(
    region_name='us-west-2', 
    aws_access_key_id=config['AWS']['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=config['AWS']['AWS_SECRET_ACCESS_KEY'],
    aws_session_token=config['AWS']['AWS_SESSION_TOKEN'],
)


#%%
song_extractor = SongExtractor()
artists_extractor = ArtistExtractor()

patterns = []

for char1 in string.ascii_uppercase:
    for char2 in string.ascii_uppercase:
        patterns.append(f"{char1}/{char2}")

for pattern in patterns:
    search_path         = f"{data_path}/{pattern}/**/*.h5"
    songs_output_path   = f"{output_path}/songs/{pattern}.json"
    artists_output_path = f"{output_path}/artists/{pattern}.json"
    songs_remote_path   = f"msd/songs/{pattern}.json"
    artists_remote_path = f"msd/artists/{pattern}.json"

    logger.info(f"Processing {search_path}")

    songs = song_extractor.extract_many_files(search_path)
    artists = artists_extractor.extract_many_files(search_path)

    if songs == []:
        continue
    else:
        song_extractor.output_json(songs, songs_output_path)
        client.upload_file(songs_output_path, bucket, songs_remote_path)

        artists_extractor.output_json(artists, artists_output_path)
        client.upload_file(artists_output_path, bucket, artists_remote_path)

# %%
