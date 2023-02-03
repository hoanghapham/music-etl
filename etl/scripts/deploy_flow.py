from pathlib import Path
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

from src.utils.custom_logger import init_logger
from flows.music_etl import music_etl


logger = init_logger(Path(__file__).name)

mapping = [
    (music_etl, 'music-etl-daily'),
]

for flow, name in mapping:

    logger.info(f"Building deployment {name}...")

    deployment = Deployment.build_from_flow(
        flow            = flow,
        name            = name,
        version         = 1,
        work_queue_name = 'default',
        schedule        = (CronSchedule(cron="0 7 * * *", timezone="UTC")),
        parameters      = {'mode': 'prod'},
        tags = ['daily']
    )

    logger.info(f"Applying deployment {name}...")
    deployment.apply()
# %%
