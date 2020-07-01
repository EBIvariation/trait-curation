"""
This module contains all the functionality that uses ZOOMA to retrieve mapping suggestions and create the suggested
terms in the app's database
"""
import requests

from ..models import Trait, MappingSuggestion, OntologyTerm, User
from .ols import make_ols_query, get_ontology_id


BASE_URL = "http://www.ebi.ac.uk/spot/zooma/v2/api"


def get_zooma_suggestions():
    """
    Retrieves zooma mapping suggestions for all traits and creates terms and suggestions in the app's database for each
    of them.
    """
    traits = Trait.objects.all()
    for trait in traits:
        suggestion_list = get_zooma_suggestions_for_trait(trait)
        for suggestion in suggestion_list:
            suggested_term_iri = suggestion["semanticTags"][0]  # E.g. http://purl.obolibrary.org/obo/HP_0004839
            suggested_term = create_local_term(suggested_term_iri)
            create_mapping_suggestion(trait, suggested_term)


def get_zooma_suggestions_for_trait(trait):
    """
    Takes in a trait object as its argument and returns the zooma response of a suggestion list as a dictionary.
    """
    formatted_trait_name = trait.name.replace(' ', '+')
    response = requests.get(
        f"{BASE_URL}/services/annotate?propertyValue={formatted_trait_name} \
        &filter=required:[none],ontologies:[efo,mondo,hp,orphanet]")
    return response.json()


def create_local_term(suggested_term_iri):
    """
    Takes in a single zooma suggestion result and creates an ontology term for it in the app's database. If that term
    already exists, returns the existing term
    """
    print(suggested_term_iri)
    if OntologyTerm.objects.filter(iri=suggested_term_iri).exists():
        return OntologyTerm.objects.filter(iri=suggested_term_iri).first()
    # Search for the term in EFO and return its information. If it is not in EFO, search for it in original ontology.
    term_info = make_ols_query(suggested_term_iri, 'efo')
    term_ontology_id = 'efo'
    # None here means that the term wasn't found in the EFO ontology
    if term_info is None:
        term_ontology_id = get_ontology_id(suggested_term_iri)
        term_info = make_ols_query(suggested_term_iri, term_ontology_id)
        # If the term is not found in the original ontology either, return
        if term_info is None:
            print(f'No info found on {suggested_term_iri}')
            return
    term_status = get_term_status(term_ontology_id, term_info['is_obsolete'])
    # Create an ontology term in the database
    term = OntologyTerm(curie=term_info['curie'], iri=suggested_term_iri, label=term_info['label'], status=term_status)
    term.save()
    return term


def get_term_status(ontology_id, is_obsolete):
    """
    Takes the ontology_id of a term and a whether it is obsolete or not, and returns its calculated status.
    'Obsolete' if the is_obsolete flag is true, 'Current' if its ontology is EFO, and 'Needs Import' otherwise
    """
    if is_obsolete:
        return 'obsolete'
    if ontology_id == 'efo':
        return 'current'
    return 'needs_import'


def create_mapping_suggestion(trait, term):
    """
    Creates a mapping suggestion in the app's database, if it doesn't exist already.
    """
    zooma = User.objects.filter(username="Zooma").first()
    if MappingSuggestion.objects.filter(trait_id=trait, term_id=term).exists():
        return
    suggestion = MappingSuggestion(trait_id=trait, term_id=term, made_by=zooma)
    suggestion.save()
