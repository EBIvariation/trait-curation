"""
This module contains all the functionality that uses ZOOMA to retrieve mapping suggestions and create the suggested
terms in the app's database.
"""
import requests
import logging

from django.db import transaction

from ..models import Trait, MappingSuggestion, OntologyTerm, User, Status, Mapping
from .ols import make_ols_query, get_ontology_id
from .oxo import make_oxo_query

logging.basicConfig()
logger = logging.getLogger('ZOOMA')
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

    datasource_suggestion_list = get_suggestions_from_datasources(trait)
    ols_suggestion_list = get_suggestions_from_ols(trait)

    high_confidence_term_iris = list()  # A list of terms with 'HIGH' mapping confidence
    final_suggestion_iri_set = set()  # A set of the term iris which are kept from the ZOOMA queries

    for suggestion in datasource_suggestion_list + ols_suggestion_list:
        if len(suggestion["semanticTags"]) > 1:
            logger.warn("Suggestion with combined terms found! Skipping suggestion...")
            continue
        suggested_term_iri = suggestion["semanticTags"][0]  # E.g. http://purl.obolibrary.org/obo/HP_0004839
        if suggestion['confidence'] == 'HIGH':
            high_confidence_term_iris.append(suggested_term_iri)
        if get_ontology_id(suggested_term_iri) in ["efo", "ordo", "hp", "mondo"]:
            final_suggestion_iri_set.add(suggested_term_iri)

    created_terms = set()
    for suggested_iri in final_suggestion_iri_set:
        suggested_term = create_local_term(suggested_iri)
        created_terms.add(suggested_term)
        create_mapping_suggestion(trait, suggested_term)
    find_automatic_mapping(trait, created_terms, high_confidence_term_iris)
    delete_unused_suggestions(trait, created_terms)


def get_suggestions_from_datasources(trait):
    """
    Takes in a trait object as its argument and returns the zooma response of a suggestion list as a dictionary.
    """
    formatted_trait_name = requests.utils.quote(trait.name)
    response = requests.get(
        f"{BASE_URL}/services/annotate?propertyValue={formatted_trait_name}"
        "&filter=required:[cttv,sysmicro,atlas,ebisc,uniprot,gwas,cbi,clinvar-xrefs]")
    return response.json()


def get_suggestions_from_ols(trait):
    """
    Takes in a trait object as its argument and returns the zooma response of a suggestion list as a dictionary.
    """
    formatted_trait_name = trait.name.replace(' ', '+')
    response = requests.get(
        f"{BASE_URL}/services/annotate?propertyValue={formatted_trait_name}"
        "&filter=required:[none],ontologies:[efo,mondo,hp,ordo]")
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


def find_automatic_mapping(trait, created_terms, high_confidence_term_iris):
    """
    If a trait is unmapped, attempts to find an automatic mapping. First if it finds a ZOOMA suggestion with 'HIGH'
    confidence, then attemps to find an exact text match.
    """
    if trait.status != Status.UNMAPPED:
        return

    # Check if a created term suggestion has 'HIGH" confidence, and map it to the trait if it does
    for term in created_terms:
        if term.iri in high_confidence_term_iris:
            create_mapping(trait, term)
            logger.info(f"CREATED HIGH CONFIDENCE MAPPING {trait.current_mapping}")
            return

    # Check if a created term suggestion is an exact text match with the trait, and map it if it does
    for term in created_terms:
        if trait.name.lower() == term.label.lower():
            create_mapping(trait, term)
            logger.info(f"CREATED EXACT TEXT MATCH MAPPING {trait.current_mapping}")
            return

    # For high confidence term suggestions that weren't in EFO compatible ontologies
    for term_iri in high_confidence_term_iris:
        # Skip medgen terms since info about them can't be retrieved through OLS
        if 'medgen' in term_iri:
            continue

        # Create term suggestion from OxO cross references
        ontology_id = get_ontology_id(term_iri)
        term_curie = make_ols_query(identifier_value=term_iri, ontology_id=ontology_id)['curie']
        oxo_results = make_oxo_query([term_curie])
        for result in oxo_results['_embedded']['searchResults'][0]['mappingResponseList']:
            ontology_id = result['targetPrefix'].lower()  # E.g. 'efo'
            if ontology_id == "orphanet":
                ontology_id = "ordo"
            result_iri = make_ols_query(identifier_value=result['curie'],
                                        ontology_id=ontology_id, identifier_type='obo_id')['iri']
            suggested_term = create_local_term(result_iri)
            created_terms.append(suggested_term)
            create_mapping_suggestion(trait, suggested_term)


@transaction.atomic
def create_mapping(trait, term):
    zooma_user = User.objects.filter(email='eva-dev@ebi.ac.uk').first()
    if Mapping.objects.filter(trait_id=trait, term_id=term).exists():
        return
    mapping = Mapping(trait_id=trait, term_id=term, curator=zooma_user, is_reviewed=False)
    mapping.save()
    trait.current_mapping = mapping
    trait.save()


def delete_unused_suggestions(trait, created_terms):
    """
    Takes in a trait and a set of created_terms, found in the previously executed ZOOMA query. This function gets all
    the mapping suggestions for that trait that are NOT found in the created_terms list or in any previous mappings
    for that trait, and deletes them
    """
    trait_mappings = trait.mapping_set.all()
    for mapping in trait_mappings:
        created_terms.add(mapping.term_id)
    deleted_suggestions = trait.mappingsuggestion_set.exclude(term_id__in=list(created_terms))
    deleted_suggestions.delete()
    logger.info(f"Deleted mapping suggestions {deleted_suggestions.all()}")
