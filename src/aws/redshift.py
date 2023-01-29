import redshift_connector
from src.utils.custom_logger import init_logger

class RedshiftConnector:

    def __init__(
            self, 
            host, 
            database='dev', 
            port: int =5439, 
            user='awsuser', 
            password=None,
            logger=None,
            autocommit=True
        ) -> None:
        if logger is None:
            self.logger = init_logger(self.__class__.__name__)
        else:
            self.logger = logger

        try:
            self.conn = redshift_connector.connect(
                host=host, database=database, port=port, user=user, password=password)
        except Exception as e:
            self.logger.error(e)
            raise e
        
        self.conn.autocommit = autocommit

    def execute_query(self, query, return_result=False):
        cursor = self.conn.cursor()

        try:
            cursor.execute(query)
        except Exception as e:
            self.logger.error(e)
            self.conn.rollback()
            return None
        else:
            if return_result:
                result = cursor.fetch_all()
                return result
            else:
                return None

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
