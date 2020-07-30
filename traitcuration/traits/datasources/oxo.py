import requests
import logging

from retry import retry

logging.basicConfig()
logger = logging.getLogger('OXO')
logger.setLevel(logging.INFO)

BASE_URL = "'https://www.ebi.ac.uk/spot/oxo/api/search?size=5000'"


@retry(tries=10, delay=5, backoff=1.2, jitter=(1, 3), logger=logger)
def make_oxo_query(ids, mapping_target, distance):
    payload = {}
    payload['ids'] = ids
    payload['mappingTarget'] = mapping_target
    payload['distance'] = distance
    result = requests.post(BASE_URL, data=payload).json()
    return result
