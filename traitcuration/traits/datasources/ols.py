"""
This module contains functions to retrieve info about terms from OLS, as well as helper functions such as
ontology_id extraction
"""
import requests
import logging
from retry import retry

from django.db import transaction

from ..models import Status, OntologyTerm


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "https://www.ebi.ac.uk/ols/api/"


@retry(tries=3, delay=5, backoff=1.2, jitter=(1, 3), logger=logger)
def make_ols_query(identifier_value, ontology_id, identifier_type='iri'):
    """
    Takes in an identifier type (iri or curie), the value for that indenrifier to query for, and the ontology id to
    search against. Returns a dictionary for that term with the fields 'label', 'obo_id' which is the CURIE and
    'is_obsolete' as True or False.
    """
    response = requests.get(f"{BASE_URL}ontologies/{ontology_id}/terms?{identifier_type}={identifier_value}")
    # 404 errors are expected. In any other case, raise an exception and retry the query
    if response.status_code == 404:
        return None
    response.raise_for_status()
    results = response.json()
    return parse_ols_results(results)


def parse_ols_results(results):
    term_info = results["_embedded"]["terms"][0]
    term_iri = term_info["iri"]  # E.g. http://www.ebi.ac.uk/efo/EFO_0000400
    term_curie = term_info["obo_id"]  # E.g. EFO:0000400
    term_label = term_info["label"]  # E.g. Diabetes mellitus
    term_is_obsolete = term_info["is_obsolete"]  # True or False value on whether the term is obsolete or not
    info_dict = {"curie": term_curie, "iri": term_iri, "label": term_label, "is_obsolete": term_is_obsolete}
    return info_dict


def get_ontology_id(term_iri):
    """
    Extracts the ontology id from the term iri, to be used for OLS queries by reading the last part of an iri and
    reading the ontology id using the term prefix
    E.g. extracts 'mondo' from http://purl.obolibrary.org/obo/MONDO_0019482
    """
    ontology_id = term_iri.split('/')[-1].split('_')[0].lower()
    # Orphanet terms use Orphanet_XXXXXXX syntax, but their OLS id is 'ordo'
    if ontology_id == 'orphanet':
        ontology_id = 'ordo'
    return ontology_id


def ols_update():
    """
    Query OLS for all terms with 'current', 'awaiting_import' and 'needs_import' status and update their status
    """
    terms_to_query = OntologyTerm.objects.filter(
        status__in=[Status.CURRENT, Status.AWAITING_IMPORT, Status.NEEDS_IMPORT])
    for term in terms_to_query:
        ols_query_term(term)


@transaction.atomic
def ols_query_term(term):
    logger.info(f"Querying OLS for term {term}")
    efo_response = make_ols_query(term.iri, 'efo')
    term_ontology_id = get_ontology_id(term.iri)
    parent_ontology_response = None
    if term_ontology_id != 'efo':
        parent_ontology_response = make_ols_query(term.iri, term_ontology_id)
    term.status = get_term_status(efo_response, parent_ontology_response, term.status)
    if term.status == Status.CURRENT:
        term.label = efo_response['label']
    elif term.status in [Status.NEEDS_IMPORT, Status.AWAITING_IMPORT]:
        term.label = parent_ontology_response['label']
    term.save()


def get_term_status(efo_response, parent_ontology_response=None, previous_status=None):
    if not efo_response and not parent_ontology_response:
        logger.info("FOUND DELETED")
        return Status.DELETED
    if efo_response and efo_response.get('is_obsolete') is True or \
            parent_ontology_response and parent_ontology_response.get('is_obsolete') is True:
        logger.info("FOUND OBSOLETE")
        return Status.OBSOLETE
    if efo_response is not None:
        return Status.CURRENT
    if not previous_status:
        return Status.NEEDS_IMPORT
    return previous_status
