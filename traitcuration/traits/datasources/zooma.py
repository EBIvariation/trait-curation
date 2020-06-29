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
        results_list = get_suggestions_for_trait(trait)
        for result in results_list:
            term = create_local_term(result)
            if term is not None:
                create_mapping_suggestion(trait, term)


def get_suggestions_for_trait(trait):
    """
    Takes in a trait object as its argument and returns the zooma response of a suggestion list as a dictionary.
    """
    formatted_trait_name = trait.name.replace(' ', '+')
    response = requests.get(
        f"{BASE_URL}/services/annotate?propertyValue={formatted_trait_name} \
        &filter=required:[none],ontologies:[efo,mondo,hp,orphanet]")
    return response.json()


def create_local_term(result):
    """
    Takes in a single zooma suggestion result and creates an ontology term for it in the app's database.
    """
    term_uri = result["semanticTags"][0]
    print(term_uri)
    if OntologyTerm.objects.filter(uri=term_uri).exists():
        return
    # Search for the term in EFO and return its information. If it is not in EFO, search for it in original ontology.
    term_info = make_ols_query(term_uri, 'efo')
    if term_info is None:
        term_info = make_ols_query(term_uri, get_ontology_id(term_uri))
        # If the term is not found in the original ontology either
        if term_info is None:
            print(f'No info found on {term_uri}')
            return
    # Create an ontology term in the database
    term = OntologyTerm(
        curie=term_info['curie'], uri=term_uri, label=term_info['label'], status=term_info['status'])
    term.save()
    return term


def create_mapping_suggestion(trait, term):
    """
    Creates a mapping suggestion in the app's database.
    """
    zooma = User.objects.filter(username="Zooma").first()
    suggestion = MappingSuggestion(trait_id=trait, term_id=term, made_by=zooma)
    suggestion.save()
