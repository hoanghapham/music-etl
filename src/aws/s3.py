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
        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger

        self.region_name = region_name

        self.client = boto3.resource(
            's3',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )

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
        except self.client.meta.client.exceptions.BucketAlreadyExists as err:
            self.logger.info(f"Bucket {bucket_name} already existed.")
    
    def upload_content_to_s3(self, bucket_name: str, file_name: str, content: str):
        """Upload string content to S3. Currently only support "new-line delimited JSON" content.

        Parameters
        ----------
        bucket_name : str
        file_name : _type_
        content : str
            New-line delimited JSON string

        """
        obj = self.client.Object(bucket_name, file_name)
        try:
            obj.put(Body=content)
        except Exception as e:
            self.logger.error(e)
            raise e
    






    

