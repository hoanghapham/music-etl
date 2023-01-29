import redshift_connector
from src.utils.custom_logger import init_logger
from logging import Logger
class RedshiftClient:
    """Custom Redshift client class"""
    def __init__(
            self, 
            host: str, 
            database: str = 'dev', 
            port: int = 5439, 
            user: str = 'awsuser', 
            password: str = None,
            logger: Logger = None,
            autocommit=True
        ) -> None:
        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger

        # Create connection
        try:
            self.conn = redshift_connector.connect(
                host=host, database=database, port=port, user=user, password=password)
            self.conn.autocommit = autocommit
        except Exception as e:
            self.logger.error(e)
            raise e

    def execute_query(self, query: str) -> list:
        """Execute a query against the Redshift database. 

        Parameters
        ----------
        query : str
        return_result : bool, optional
            Default: False. If True, return the result of the query.

        Returns
        -------
        list
            A list containing rows of the query result
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute(query)
        except Exception as e:
            self.logger.error(e)
            self.conn.rollback()
            return None
        else:
            result = cursor.fetch_all()
            return result

    def create_table(self):
        pass

    def delete_table(self):
        pass

    def full_refresh_load(self):
        pass

    def incremental_load(self):
        pass

    def append_load(self):
        pass
        
    def copy_s3_to_redshift(self):
        pass
