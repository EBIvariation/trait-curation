"""
This module contains functions to retrieve info about terms from OLS, as well as helper functions such as
ontology_id extraction
"""
import requests
import logging

from retry import retry

logging.basicConfig()
logger = logging.getLogger('ZOOMA')
logger.setLevel(logging.INFO)

BASE_URL = "https://www.ebi.ac.uk/ols/api/"


@retry(tries=10, delay=5, backoff=1.2, jitter=(1, 3), logger=logger)
def make_ols_query(term_iri, ontology_id):
    """
    Takes in a term iri (or IRI as referenced in OLS documentation) and the ontology id to search against. Returns a
    dictionary for that term with the fields 'label', 'obo_id' which is the CURIE and 'is_obsolete' as True or False.
    """
    response = requests.get(f"{BASE_URL}ontologies/{ontology_id}/terms?iri={term_iri}")
    # 404 errors are expected. In any other case, raise an exception and retry the query
    if response.status_code == 404:
        return None
    response.raise_for_status()
    results = response.json()
    term_info = results["_embedded"]["terms"][0]
    term_curie = term_info["obo_id"]  # E.g. EFO:0000400
    term_label = term_info["label"]  # E.g. Diabetes mellitus
    term_is_obsolete = term_info["is_obsolete"]  # True or False value on whether the term is obsolete or not
    info_dict = {"curie": term_curie, "label": term_label, "is_obsolete": term_is_obsolete}
    return info_dict


def get_ontology_id(term_iri):
    """
    Extracts the ontology id from the term iri, to be used for OLS queries by reading the last part of an iri and
    reading the ontology id using the term prefix
    E.g. extracts 'mondo' from http://purl.obolibrary.org/obo/MONDO_0019482
    """
    ontology_id = term_iri.split('/')[-1].split('_')[0].lower()
    # Orphanet terms use Orphanet_XXXXXXX syntax, but their OLS id is 'ordo'
    if ontology_id == 'Orphanet':
        ontology_id = 'ordo'
    return ontology_id
