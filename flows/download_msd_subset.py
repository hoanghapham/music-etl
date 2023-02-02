#%%
from src.bash_operator import BashOperator


bash = BashOperator()

data_path = "/media/hapham/data/projects/data"

bash.download_file(
    "http://labrosa.ee.columbia.edu/~dpwe/tmp/millionsongsubset.tar.gz", 
    f"{data_path}/millionsongsubset.tar.gz"
)

bash.extract_file(f"{data_path}/millionsongsubset.tar.gz", data_path)