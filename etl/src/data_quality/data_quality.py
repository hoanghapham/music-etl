from src.aws.redshift import RedshiftClient
from logging import Logger
from src.utils.custom_logger import init_logger
from src.data_quality.tests import Test

class DataQualityOperator:
    """Class to run data tests"""

    def __init__(self, client: RedshiftClient, logger: Logger = None):
        self.logger = logger or init_logger(self.__class__.__name__)
        self.client = client

    def run_test(self, test: Test) -> bool:
        """Run a single test.

        Parameters
        ----------
        test : Test
            Test object coming from the `tests` module

        Returns
        -------
        bool
            Return True if the test passes, False otherwise.
        """        
        try:
            result = self.client.execute_query(test.query)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            if len(result) == 0:
                self.logger.info(f"Data test {test.name} PASSED.")
                return True
            else:
                self.logger.info(f"Data test {test.name} FAIED.")
                return False

    def run_multi_tests(self, tests: list[Test]):
        """Iterate through a list of Test objects, run and report results.

        Parameters
        ----------
        tests : list[Test]

        Raises
        ------
        ValueError
            Raise this exception to alert that the data test has failed.
        """

        all_tests = []
        failed_tests = []
        
        for test in tests:
            result = self.run_test(test)
            all_tests.append({'name': test.name, 'result': result})
            
            if result is False:
                failed_tests.append(test.name)

        if len(failed_tests) > 0:
            message = f"There are {len(failed_tests)} failed data test(s): {', '.join(failed_tests)}"
            self.logger.error(message)
            raise ValueError(message)
        else:
            self.logger.info("All data tests has PASSED.")

            
