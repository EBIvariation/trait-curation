import requests


BASE_URL = "https://www.ebi.ac.uk/ols/api/"


def make_ols_query(term_iri, ontology_id):
    """
    Takes in a term iri (or IRI as referenced in OLS documentation) and the ontology id to search against. Returns a
    dictionary for that term with the fields 'label', 'obo_id' which is the CURIE and 'status'.
    """
    results = requests.get(f"{BASE_URL}ontologies/{ontology_id}/terms?iri={term_iri}").json()
    print(results)
    if 'error' in results:
        print
        return None
    term_info = results["_embedded"]["terms"][0]
    term_curie = term_info["obo_id"]  # E.g. EFO:0000400
    term_label = term_info["label"]  # E.g. Diabetes mellitus
    term_is_obsolete = term_info["is_obsolete"]  # True or False value on whether the term is obsolete or not
    term_status = get_term_status(ontology_id, term_is_obsolete)
    info_dict = {"curie": term_curie, "label": term_label, "status": term_status}
    print(info_dict)
    print()
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
