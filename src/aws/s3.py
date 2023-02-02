import boto3
from src.utils.custom_logger import init_logger

class S3Client:
    """Custom S3 client class"""

    def __init__(
        self,
            region_name: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            aws_session_token: str = None,
            logger = None
        ):
        self.logger = logger or init_logger(self.__class__.__name__)

        self.region_name = region_name

        try:
            self.client = boto3.client(
                's3',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token
            )
            self.logger.info("Connected to S3")
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Failed to connect to S3")
            raise e

    def create_bucket(self, bucket_name: str) -> None:
        """Create an S3 bucket if it doesn't already exist.

        Parameters
        ----------
        bucket_name : str
        """        
        try:
            self.client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.region_name
                }
            )
        except (
            self.client.exceptions.BucketAlreadyExists, 
            self.client.exceptions.BucketAlreadyOwnedByYou
        ) as err:
            self.logger.info(f"Bucket {bucket_name} already existed.")
    
    def upload_content(self, content: str, bucket_name: str, file_name: str):
        """Upload string content to S3. Currently only support "new-line delimited JSON" content.

        Parameters
        ----------
        content : str
            New-line delimited JSON string
        bucket_name : str
        file_name : str

        """
        obj = self.client.Object(bucket_name, file_name)
        try:
            obj.put(Body=content)
        except Exception as e:
            self.logger.error(e)
            raise e
    
    def upload_file(self, input_file_path: str, bucket_name: str, file_path: str):
        try:
            self.client.upload_file(input_file_path, bucket_name, file_path)
            self.logger.info(f"File uploaded to s3://{bucket_name}/{file_path}")
        except Exception as e:
            self.logger.error(e)
            raise e


    def download_file(self, bucket_name: str, file_path: str, output_file_path: str):
        try:
            self.client.download_file(bucket_name, file_path, output_file_path)
        except Exception as e:
            self.logger.error(e)
            raise e



    

