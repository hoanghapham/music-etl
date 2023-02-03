#%%
from flows.music_etl import music_etl
from prefect.deployments import Deployment
from src.utils.custom_logger import init_logger

logger = init_logger(__name__)

logger.info(f"Building deployment for music_etl flow...")

deployment = Deployment.build_from_flow(
    flow            = music_etl,
    name            = 'adhoc',
    version         = 1,
    work_queue_name = 'default',
    tags            = ['local']
)

logger.info("Deploying music_etl flow...")
deployment.apply()
