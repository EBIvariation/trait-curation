"""
This module holds dummy data to import during development
"""
from ..models import OntologyTerm, MappingSuggestion, Trait, Mapping, User, Review


def import_dummy_data():
    Review.objects.all().delete()
    MappingSuggestion.objects.all().delete()
    Mapping.objects.all().delete()
    Trait.objects.all().delete()
    OntologyTerm.objects.all().delete()
    User.objects.all().delete()
    # ONTOLOGY TERMS
    term_current1 = OntologyTerm(label='/ Diabetes mellitus /', curie='EFO:0000400',
                                 iri='http://www.ebi.ac.uk/efo/EFO_0000400', status='current')
    term_current1.save()
    term_current2 = OntologyTerm(label='/ digestive system disease /', curie='EFO:0000405',
                                 iri='http://www.ebi.ac.uk/efo/EFO_0000405', status='current')
    term_current2.save()
    term_ni1 = OntologyTerm(label='/ Insulin-resistant diabetes mellitus /', curie='HP:0000831',
                            iri='http://purl.obolibrary.org/obo/HP_0000831', status='needs_import')
    term_ni1.save()
    term_ni2 = OntologyTerm(label='/ breast-ovarian cancer, familial, susceptibility to, 3 /', curie='MONDO:0013253',
                            iri='http://purl.obolibrary.org/obo/MONDO_0013253', status='needs_import')
    term_ni2.save()
    term_ai2 = OntologyTerm(label='/ pancreatic cancer, susceptibility to, 4 /', curie='MONDO:0013685',
                            iri='http://purl.obolibrary.org/obo/MONDO_0013685', status='awaiting_import')
    term_ai2.save()
    term_nc1 = OntologyTerm(label='/ Hypogonadism, diabetes mellitus, alopecia, mental retardation and \
          electrocardiographic abnormalities', description='The description for Hypogonadism, diabetes \
          mellitus, alopecia, mental retardation and electrocardiographic abnormalities ',
                            cross_refs='MONDO:0013685,HP:0000400', status='awaiting_creation')
    term_nc1.save()
    term_nc2 = OntologyTerm(label='/ Familial cancer of breast, 2 /',
                            description='Description for familial cancer of breast, 2',
                            cross_refs="Orphanet:0000405", status='awaiting_creation')
    term_nc2.save()
    term_ac1 = OntologyTerm(label='/ Diastrophic dysplasia /',
                            description='Description for Diastrophic dysplasia',
                            cross_refs="", status='awaiting_creation')
    term_ac1.save()
    term_obsolete = OntologyTerm(label='/ Diastrophic dysplasia /', curie='Orphanet:628',
                                 iri='http://www.orpha.net/ORDO/Orphanet_628', status='obsolete')
    term_obsolete.save()
    term_deleted = OntologyTerm(label='/ Spastic paraplegia /', curie='HP:0001258',
                                iri=' http://purl.obolibrary.org/obo/HP_0001258', status='deleted')
    term_deleted.save()
    # TRAITS
    trait_current = Trait(name='/ Diabetes mellitus /', status='current', number_of_source_records=9)
    trait_current.save()
    trait_ar1 = Trait(name='/ digestive system disease /', status='awaiting_review', number_of_source_records=4)
    trait_ar1.save()
    trait_needs_import = Trait(name='/ Familial cancer of breast /', status='needs_import', number_of_source_records=5)
    trait_needs_import.save()
    trait_ar2 = Trait(name='/ Insulin-resistant diabetes mellitus /', status='awaiting_review', number_of_source_records=1)
    trait_ar2.save()
    trait_ai = Trait(name='/ pancreatic cancer, susceptibility to, 4 /',
                     status='awaiting_import', number_of_source_records=5)
    trait_ai.save()
    trait_nc = Trait(name='/ Hypogonadism, diabetes mellitus, alopecia, mental retardation and \
          electrocardiographic abnormalities /', status='needs_creation', number_of_source_records=12)
    trait_nc.save()
    trait_ar3 = Trait(name='/ Pancreatic cancer 4 /', status='awaiting_review', number_of_source_records=1)
    trait_ar3.save()
    trait_ac = Trait(name='/ Familial cancer of breast /', status='awaiting_creation', number_of_source_records=4)
    trait_ac.save()
    trait_obsolete = Trait(name='/ Diastrophic dysplasia /', status='obsolete', number_of_source_records=7)
    trait_obsolete.save()
    trait_deleted = Trait(name='/ Spastic paraplegia /', status='deleted', number_of_source_records=7)
    trait_deleted.save()
    # USERS
    user1 = User(username='/ user1', email='user1@user.com')
    user1.save()
    user2 = User(username='/ user2', email='user2@user.com')
    user2.save()
    user3 = User(username='/ user3', email='user3@user.com')
    user3.save()
    # MAPPINGS
    m1 = Mapping(trait_id=trait_current, term_id=term_current1, curator=user1, is_reviewed=True)
    m1.save()
    trait_current.current_mapping = m1
    trait_current.save()
    m2 = Mapping(trait_id=trait_ar1, term_id=term_current2, curator=user2, is_reviewed=False)
    m2.save()
    trait_ar1.current_mapping = m2
    trait_ar1.save()
    m3 = Mapping(trait_id=trait_needs_import, term_id=term_ni1, curator=user3, is_reviewed=True)
    m3.save()
    trait_needs_import.current_mapping = m3
    trait_needs_import.save()
    m4 = Mapping(trait_id=trait_ar2, term_id=term_ni2, curator=user1, is_reviewed=False)
    m4.save()
    trait_ar2.current_mapping = m4
    trait_ar2.save()
    m5 = Mapping(trait_id=trait_ai, term_id=term_ai2, curator=user2, is_reviewed=True)
    m5.save()
    trait_ai.current_mapping = m5
    trait_ai.save()
    m6 = Mapping(trait_id=trait_nc, term_id=term_nc1, curator=user3, is_reviewed=True)
    m6.save()
    trait_nc.current_mapping = m6
    trait_nc.save()
    m7 = Mapping(trait_id=trait_ar3, term_id=term_nc2, curator=user1, is_reviewed=False)
    m7.save()
    trait_ar3.current_mapping = m7
    trait_ar3.save()
    m8 = Mapping(trait_id=trait_ac, term_id=term_ac1, curator=user2, is_reviewed=True)
    m8.save()
    trait_ac.current_mapping = m8
    trait_ac.save()
    m9 = Mapping(trait_id=trait_obsolete, term_id=term_obsolete, curator=user2, is_reviewed=True)
    m9.save()
    trait_obsolete.current_mapping = m9
    trait_obsolete.save()
    m10 = Mapping(trait_id=trait_deleted, term_id=term_deleted, curator=user2, is_reviewed=True)
    m10.save()
    trait_deleted.current_mapping = m10
    trait_deleted.save()
    # REVIEWS
    r = Review(mapping_id=m1, reviewer=user2)
    r.save()
    r = Review(mapping_id=m1, reviewer=user3)
    r.save()
    r = Review(mapping_id=m3, reviewer=user1)
    r.save()
    r = Review(mapping_id=m3, reviewer=user2)
    r.save()
    r = Review(mapping_id=m5, reviewer=user1)
    r.save()
    r = Review(mapping_id=m5, reviewer=user3)
    r.save()
    r = Review(mapping_id=m6, reviewer=user1)
    r.save()
    r = Review(mapping_id=m6, reviewer=user2)
    r.save()
    r = Review(mapping_id=m8, reviewer=user1)
    r.save()
    r = Review(mapping_id=m8, reviewer=user3)
    r.save()
    r = Review(mapping_id=m9, reviewer=user1)
    r.save()
    r = Review(mapping_id=m9, reviewer=user3)
    r.save()
    r = Review(mapping_id=m10, reviewer=user1)
    r.save()
    r = Review(mapping_id=m10, reviewer=user3)
    r.save()
