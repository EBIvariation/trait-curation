"""
This module contains all the functionality that uses ZOOMA to retrieve mapping suggestions and create the suggested
terms in the app's database.
"""
import requests
import logging

from django.db import transaction

from ..models import Trait, MappingSuggestion, OntologyTerm, User
from .ols import make_ols_query, get_ontology_id, get_term_status

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "http://www.ebi.ac.uk/spot/zooma/v2/api"


def run_zooma_for_all_traits():
    """
    Retrieves zooma mapping suggestions for all traits and creates terms and suggestions in the app's database for each
    of them.
    """
    traits = Trait.objects.all()
    for trait in traits:
        run_zooma_for_single_trait(trait)


def run_zooma_for_single_trait(trait):
    logger.info(f"Retrieving ZOOMA suggestions for trait: {trait.name}")
    suggestion_list = get_zooma_suggestions_for_trait(trait)
    # A set of suggested terms found in the query, used to exclude those terms from being deleted from the database
    # when the delete_unused_mappings function is called.
    suggested_terms = set()
    for suggestion in suggestion_list:
        suggested_term_iri = suggestion["semanticTags"][0]  # E.g. http://purl.obolibrary.org/obo/HP_0004839
        suggested_term = create_local_term(suggested_term_iri)
        create_mapping_suggestion(trait, suggested_term)
        suggested_terms.add(suggested_term)
    delete_unused_suggestions(trait, suggested_terms)


def get_zooma_suggestions_for_trait(trait):
    """
    Takes in a trait object as its argument and returns the zooma response of a suggestion list as a dictionary.
    """
    formatted_trait_name = trait.name.replace(' ', '+')
    response = requests.get(
        f"{BASE_URL}/services/annotate?propertyValue={formatted_trait_name} \
        &filter=required:[none],ontologies:[efo,mondo,hp,ordo]")
    return response.json()


@transaction.atomic
def create_local_term(suggested_term_iri):
    """
    Takes in a single zooma suggestion result and creates an ontology term for it in the app's database. If that term
    already exists, returns the existing term
    """
    logger.info(f"Retrieving info for suggested term: {suggested_term_iri}")
    if OntologyTerm.objects.filter(iri=suggested_term_iri).exists():
        logger.info(f"Term {suggested_term_iri} already exists in the database")
        return OntologyTerm.objects.filter(iri=suggested_term_iri).first()
    # Search for the term in EFO and return its information. If it is not in EFO, search for it in original ontology.
    term_info = make_ols_query(suggested_term_iri, 'efo')
    term_ontology_id = 'efo'
    # None here means that the term wasn't found in the EFO ontology.
    if term_info is None:
        term_ontology_id = get_ontology_id(suggested_term_iri)
        term_info = make_ols_query(suggested_term_iri, term_ontology_id)
        # If the term is not found in the original ontology either, create a 'deleted' term.
        if term_info is None:
            term_ontology_id = None
            term_info = {'curie': None, 'label': 'Not Found', 'is_obsolete': False}
            print(term_info)
    logger.info(f"Term {suggested_term_iri} found in {term_ontology_id} ontology")
    term_status = get_term_status(term_info['is_obsolete'], term_ontology_id)
    # Create an ontology term in the database
    term = OntologyTerm(curie=term_info['curie'], iri=suggested_term_iri, label=term_info['label'], status=term_status)
    term.save()
    return term


@transaction.atomic
def create_mapping_suggestion(trait, term, user_email='eva-dev@ebi.ac.uk'):
    """
    Creates a mapping suggestion in the app's database, if it doesn't exist already.
    """
    user = User.objects.filter(email=user_email).first()
    if user_email == "eva-dev@ebi.ac.uk" and user is None:
        zooma = User(first_name="ZOOMA", email="eva-dev@ebi.ac.uk")
        zooma.save()
    if MappingSuggestion.objects.filter(trait_id=trait, term_id=term).exists():
        logger.info(f"Mapping suggestion {trait} - {term} already exists in the database")
        return
    suggestion = MappingSuggestion(trait_id=trait, term_id=term, made_by=user)
    suggestion.save()
    logger.info(f"Created mapping suggestion {suggestion}")


@transaction.atomic
def delete_unused_suggestions(trait, suggested_terms):
    """
    Takes in a trait and a set of suggested_terms, found in the previously executed ZOOMA query. This function gets all
    the mapping suggestions for that trait that are NOT found in the suggested_terms list or in any previous mappings
    for that trait, and deletes them
    """
    trait_mappings = trait.mapping_set.all()
    for mapping in trait_mappings:
        suggested_terms.add(mapping.term_id)
    deleted_suggestions = trait.mappingsuggestion_set.exclude(term_id__in=list(suggested_terms))
    deleted_suggestions.delete()
    logger.info(f"Deleted mapping suggestions {deleted_suggestions}")
