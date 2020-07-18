"""
This module holds dummy data to import during development
"""
from ..models import OntologyTerm, MappingSuggestion, Trait, Mapping, User, Review, Status


def import_dummy_data():
    Review.objects.all().delete()
    MappingSuggestion.objects.all().delete()
    Mapping.objects.all().delete()
    Trait.objects.all().delete()
    OntologyTerm.objects.all().delete()
    User.objects.all().delete()
    # ONTOLOGY TERMS
    term1 = OntologyTerm(label='/ Diabetes mellitus /', curie='EFO:0000400',
                         iri='http://www.ebi.ac.uk/efo/EFO_0000400', status=Status.CURRENT)
    term2 = OntologyTerm(label='/ digestive system disease /', curie='EFO:0000405',
                         iri='http://www.ebi.ac.uk/efo/EFO_0000405', status=Status.CURRENT)
    term3 = OntologyTerm(label='/ Insulin-resistant diabetes mellitus /', curie='HP:0000831',
                         iri='http://purl.obolibrary.org/obo/HP_0000831', status=Status.NEEDS_IMPORT)
    term4 = OntologyTerm(label='/ breast-ovarian cancer, familial, susceptibility to, 3 /', curie='MONDO:0013253',
                         iri='http://purl.obolibrary.org/obo/MONDO_0013253', status=Status.NEEDS_IMPORT)
    term5 = OntologyTerm(label='/ pancreatic cancer, susceptibility to, 4 /', curie='MONDO:0013685',
                         iri='http://purl.obolibrary.org/obo/MONDO_0013685', status=Status.AWAITING_IMPORT)
    term6 = OntologyTerm(label='/ Hypogonadism, diabetes mellitus, alopecia, mental retardation and \
          electrocardiographic abnormalities', description='The description for Hypogonadism, diabetes \
          mellitus, alopecia, mental retardation and electrocardiographic abnormalities ',
                         cross_refs='MONDO:0013685,HP:0000400', status=Status.AWAITING_CREATION)
    term7 = OntologyTerm(label='/ Familial cancer of breast, 2 /',
                         description='Description for familial cancer of breast, 2',
                         cross_refs="Orphanet:0000405", status=Status.AWAITING_CREATION)
    term8 = OntologyTerm(label='/ Diastrophic dysplasia /',
                         description='Description for Diastrophic dysplasia',
                         cross_refs="", status=Status.AWAITING_CREATION)
    term9 = OntologyTerm(label='/ obsolete_adrenocortical carcinoma /', curie='EFO:0003093',
                         iri='http://www.ebi.ac.uk/efo/EFO_0003093', status=Status.OBSOLETE)
    term10 = OntologyTerm(label='/ Spastic paraplegia /', curie='HP:999999999',
                                iri=' http://purl.obolibrary.org/obo/HP_999999999', status=Status.DELETED)
    for term in (term1, term2, term3, term4, term5, term6, term7, term8, term9, term10):
        term.save()
    # TRAITS
    trait1 = Trait(name='/ Diabetes mellitus /', status=Status.CURRENT, number_of_source_records=9)
    trait2 = Trait(name='/ digestive system disease /', status='awaiting_review', number_of_source_records=4)
    trait3 = Trait(name='/ Familial cancer of breast /', status=Status.NEEDS_IMPORT, number_of_source_records=5)
    trait4 = Trait(name='/ Insulin-resistant diabetes mellitus /', status='awaiting_review', number_of_source_records=1)
    trait5 = Trait(name='/ pancreatic cancer, susceptibility to, 4 /',
                   status=Status.AWAITING_IMPORT, number_of_source_records=5)
    trait6 = Trait(name='/ Hypogonadism, diabetes mellitus, alopecia, mental retardation and \
          electrocardiographic abnormalities /', status='needs_creation', number_of_source_records=12)
    trait7 = Trait(name='/ Pancreatic cancer 4 /', status='awaiting_review', number_of_source_records=1)
    trait8 = Trait(name='/ Familial cancer of breast /', status=Status.AWAITING_CREATION, number_of_source_records=4)
    trait9 = Trait(name='/ Diastrophic dysplasia /', status='obsolete', number_of_source_records=7)
    trait10 = Trait(name='/ Spastic paraplegia /', status='deleted', number_of_source_records=7)
    for trait in (trait1, trait2, trait3, trait4, trait5, trait6, trait7, trait8, trait9, trait10):
        trait.save()
    # USERS
    user1 = User(email='user1@user.com', first_name="John", last_name="Doe")
    user2 = User(email='user2@user.com', first_name="Jane", last_name="Doe")
    user3 = User(email='user3@user.com', first_name="Jack", last_name="Doe")
    user4 = User(email="eva-dev@ebi.ac.uk", first_name="ZOOMA")
    for user in (user1, user2, user3, user4):
        user.save()
    # MAPPINGS
    m1 = Mapping(trait_id=trait1, term_id=term1, curator=user1, is_reviewed=True)
    m2 = Mapping(trait_id=trait2, term_id=term2, curator=user2, is_reviewed=False)
    m3 = Mapping(trait_id=trait3, term_id=term3, curator=user3, is_reviewed=True)
    m4 = Mapping(trait_id=trait4, term_id=term4, curator=user1, is_reviewed=False)
    m5 = Mapping(trait_id=trait5, term_id=term5, curator=user2, is_reviewed=True)
    m6 = Mapping(trait_id=trait6, term_id=term6, curator=user3, is_reviewed=True)
    m7 = Mapping(trait_id=trait7, term_id=term7, curator=user1, is_reviewed=False)
    m8 = Mapping(trait_id=trait8, term_id=term8, curator=user2, is_reviewed=True)
    m9 = Mapping(trait_id=trait9, term_id=term9, curator=user2, is_reviewed=True)
    m10 = Mapping(trait_id=trait10, term_id=term10, curator=user2, is_reviewed=True)
    for mapping in (m1, m2, m3, m4, m5, m6, m7, m8, m9, m10):
        mapping.save()
    # MAPPING SUGGESTIONS
    ms1 = MappingSuggestion(trait_id=trait1, term_id=term1, made_by=user4)
    ms2 = MappingSuggestion(trait_id=trait2, term_id=term2, made_by=user4)
    ms3 = MappingSuggestion(trait_id=trait3, term_id=term3, made_by=user4)
    ms4 = MappingSuggestion(trait_id=trait4, term_id=term4, made_by=user4)
    ms5 = MappingSuggestion(trait_id=trait5, term_id=term5, made_by=user4)
    ms6 = MappingSuggestion(trait_id=trait6, term_id=term6, made_by=user4)
    ms7 = MappingSuggestion(trait_id=trait7, term_id=term7, made_by=user4)
    ms8 = MappingSuggestion(trait_id=trait8, term_id=term8, made_by=user4)
    ms9 = MappingSuggestion(trait_id=trait9, term_id=term9, made_by=user4)
    ms10 = MappingSuggestion(trait_id=trait10, term_id=term10, made_by=user4)
    for mapping_suggestion in (ms1, ms2, ms3, ms4, ms5, ms6, ms7, ms8, ms9, ms10):
        mapping_suggestion.save()
    # SAVE CURRENT MAPPINGS
    for i in range(1, 10):
        trait = eval('trait' + str(i))
        mapping = eval('m' + str(i))
        trait.current_mapping = mapping
        trait.save()
    # REVIEWS
    reviews = list()
    reviews.append(Review(mapping_id=m1, reviewer=user2))
    reviews.append(Review(mapping_id=m1, reviewer=user3))
    reviews.append(Review(mapping_id=m3, reviewer=user1))
    reviews.append(Review(mapping_id=m3, reviewer=user2))
    reviews.append(Review(mapping_id=m5, reviewer=user1))
    reviews.append(Review(mapping_id=m5, reviewer=user3))
    reviews.append(Review(mapping_id=m6, reviewer=user1))
    reviews.append(Review(mapping_id=m6, reviewer=user2))
    reviews.append(Review(mapping_id=m8, reviewer=user1))
    reviews.append(Review(mapping_id=m8, reviewer=user3))
    reviews.append(Review(mapping_id=m9, reviewer=user1))
    reviews.append(Review(mapping_id=m9, reviewer=user3))
    reviews.append(Review(mapping_id=m10, reviewer=user1))
    reviews.append(Review(mapping_id=m10, reviewer=user3))
    for review in reviews:
        review.save()
