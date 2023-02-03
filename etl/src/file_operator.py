import subprocess
import os
from logging import Logger
from src.utils.custom_logger import init_logger

class FileOperator():

    def __init__(self, logger: Logger = None):
        self.logger = logger or init_logger(self.__class__.__name__)

    def download_file(self, url, output_file_path):
        self.logger.info("Downloading file...")
        subprocess.run(["wget", url, "-O", output_file_path])
        return output_file_path

    def extract_file(self, input_file_path, output_folder):
        self.logger.info(f"Extracting file {input_file_path} to {output_folder}...")
        os.makedirs(output_folder, exist_ok=True)
        
        try:
            subprocess.run(["tar", "-zxf", input_file_path, "-C", output_folder])
        except Exception as e:
            self.logger.error("Extracting failed.")
            self.logger.error(e)