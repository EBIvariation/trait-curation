import requests


BASE_URL = "https://www.ebi.ac.uk/ols/api/"


def make_ols_query(term_uri, ontology):
    """
    Takes in a term URI (or IRI as referenced in OLS documentation) and the ontology id to search against. Returns a
    dictionary for that term with the fields 'label', 'obo_id' which is the CURIE and 'status'.
    """
    results = requests.get(
        f"{BASE_URL}ontologies/{ontology}/terms?iri={term_uri}").json()
    print(f"{BASE_URL}ontologies/{ontology}/terms?iri={term_uri}")
    if 'error' in results:
        return None
    term_info = results["_embedded"]["terms"][0]
    term_curie = term_info["obo_id"]
    term_label = term_info["label"]
    term_status = 'current' if ontology == 'efo' else 'needs_import'
    if term_info["is_obsolete"]:
        term_status = "obsolete"
    info_dict = {"curie": term_curie,
                 "label": term_label, "status": term_status}
    print(info_dict)
    print()
    return info_dict


def get_ontology_id(term_uri):
    """
    Extracts the ontology id from the term uri, to be used for OLS queries
    """
    ontology_id = term_uri.split('/')[-1].split('_')[0].lower()
    if ontology_id == 'Orphanet':
        ontology_id = 'ordo'
    return ontology_id
