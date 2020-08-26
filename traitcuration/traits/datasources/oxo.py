import requests
import logging

from retry import retry
from django_admin_conf_vars.global_vars import config


logging.basicConfig()
logger = logging.getLogger('OXO')
logger.setLevel(logging.INFO)

BASE_URL = config.OXO_BASE_URL
MAPPING_DISTANCE = int(config.OXO_MAPPING_DISTANCE)


@retry(tries=10, delay=5, backoff=1.2, jitter=(1, 3), logger=logger)
def make_oxo_query(ids, mapping_target='Orphanet,efo,hp,mondo', distance=MAPPING_DISTANCE):
    payload = {}
    payload['ids'] = ids
    payload['mappingTarget'] = mapping_target
    payload['distance'] = distance
    result = requests.post(BASE_URL, data=payload).json()
    return result
