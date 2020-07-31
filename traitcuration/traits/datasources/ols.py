"""
This module contains functions to retrieve info about terms from OLS, as well as helper functions such as
ontology_id extraction
"""
import requests
import logging

from retry import retry

from ..models import Status, OntologyTerm


logging.basicConfig()
logger = logging.getLogger('OLS')
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


def get_term_status(is_obsolete, ontology_id=None):
    """
    Takes the ontology_id of a term and a whether it is obsolete or not, and returns its calculated status.
    'Obsolete' if the is_obsolete flag is true, 'Deleted' if no info was found in any ontology, 'Current' if its
    ontology is EFO, and 'Needs Import' if info about the term was found in another ontology.
    """
    if ontology_id is None:
        return Status.DELETED
    if is_obsolete:
        return Status.OBSOLETE
    if ontology_id == 'efo':
        return Status.CURRENT
    return Status.NEEDS_IMPORT


def check_awaiting_import_terms():
    """
    Checks if terms with the 'awaiting_import' status are now found in EFO, and if they are, assigns them as 'current'.
    """
    logger.info('CHECKING AWAITING IMPORT TERMS')
    awaiting_import_terms = OntologyTerm.objects.filter(status=Status.AWAITING_IMPORT)
    for term in awaiting_import_terms:
        logger.info(f"Checking term {term.iri}")
        term_info = make_ols_query(term.iri, 'efo')
        if term_info is not None:
            term.status = get_term_status(term_info['is_obsolete'], 'efo')
            term.save()


def check_term_status():
    """
    Queries OLS for terms with the 'awaiting_import', 'needs_import' and 'current' status, in their parent ontology,
    to determine whether they have become obsolete or deleted.
    """
    logger.info('CHECKING ALL TERM STATUS')
    terms = OntologyTerm.objects.filter(
        status__in=[Status.AWAITING_IMPORT, Status.NEEDS_IMPORT, Status.CURRENT])
    for term in terms:
        logger.info(f"Checking term {term.iri}")
        term_ontology_id = get_ontology_id(term.iri)
        term_info = make_ols_query(term.iri, term_ontology_id)
        if term_info is not None:
            term.status = get_term_status(term_info['is_obsolete'], term_ontology_id)
        else:
            term.status = Status.DELETED
        term.save()
