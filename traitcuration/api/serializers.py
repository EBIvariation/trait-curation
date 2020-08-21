from traitcuration.traits.models import Trait, Mapping, OntologyTerm, User
from rest_framework import serializers


class TraitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trait
        fields = ['name', 'current_mapping', 'status',
                  'number_of_source_records', 'timestamp_added', 'timestamp_updated']


class MappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mapping
        fields = ['trait_id', 'term_id', 'is_reviewed']
        depth = 1


class OntologyTermSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OntologyTerm
        fields = ['id', 'curie', 'iri', 'label', 'status', 'description', 'cross_refs']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
