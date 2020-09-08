from traitcuration.traits.models import Trait, Mapping, OntologyTerm, User
from rest_framework import serializers


class OntologyTermSerializer(serializers.ModelSerializer):
    term_id = serializers.IntegerField(source='id')

    class Meta:
        model = OntologyTerm
        fields = ['term_id', 'curie', 'iri', 'label', 'status', 'description', 'cross_refs']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class MappingSerializer(serializers.ModelSerializer):
    mapping_id = serializers.IntegerField(source='id')
    mapped_term = OntologyTermSerializer()

    class Meta:
        model = Mapping
        fields = ['mapping_id', 'mapped_term', 'is_reviewed']
        depth = 1


class TraitSerializer(serializers.ModelSerializer):
    trait_id = serializers.IntegerField(source='id')
    current_mapping = MappingSerializer()

    class Meta:
        model = Trait
        fields = ['trait_id', 'name', 'current_mapping', 'status', 'number_of_source_records']
        depth = 2
