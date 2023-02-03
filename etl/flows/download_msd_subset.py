from src.file_operator import FileOperator
from configparser import ConfigParser
from pathlib import Path

p = Path(__file__).with_name('config.cfg')

config = ConfigParser()
config.read(p)
data_dir = config['DATA']['DATA_DIR']
file_op = FileOperator()

if not Path(f"{data_dir}/millionsongsubset.tar.gz").exists():
    file_op.download_file(
        "http://labrosa.ee.columbia.edu/~dpwe/tmp/millionsongsubset.tar.gz", 
        f"{data_dir}/millionsongsubset.tar.gz"
    )

file_op.extract_file(f"{data_dir}/millionsongsubset.tar.gz", data_dir)