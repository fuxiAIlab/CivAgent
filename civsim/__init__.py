import sys
from loguru import logger
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--log', default='INFO', help='Set the logging level')
args = parser.parse_args()
# logger = logging.getLogger('civsim')
# logging.basicConfig(level=getattr(logging, args.log.upper()), format='%(asctime)s - %(name)s - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s')

format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{file.name}</cyan>:<cyan>{line}</cyan> | "
    "<blue>{name}</blue> | "
    "<magenta>{extra[game_id]}</magenta> | "
    "{message}"
)
logger.remove()
logger.add("logs/error.log", level="ERROR", format=format, rotation="1 day", retention="90 days", enqueue=True)
# split by day
logger.add("logs/app_{time:YYYY-MM-DD}.log", format=format, rotation="1 day", retention="30 days", enqueue=True)
# std out
logger.add(sys.stdout, format=format, level=args.log.upper(), enqueue=False)
logger = logger.bind(**{"game_id": "0"})

# set default CIVAGENT_CONFIG_PATH when not set
current_file_path = os.path.realpath(__file__)
config_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), '..', 'config.yaml'))
if 'CIVAGENT_CONFIG_PATH' not in os.environ:
    os.environ['CIVAGENT_CONFIG_PATH'] = config_path
if (config_path and os.path.exists(config_path)) is False:
    logger.debug("Error: Config file does not exist at", config_path)
