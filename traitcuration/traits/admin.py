from django.contrib import admin
from traitcuration.traits.models import Trait, User, OntologyTerm, Mapping, MappingSuggestion, Comment, Review
# Register your models here.

admin.site.register(Trait)
admin.site.register(User)
admin.site.register(Mapping)
admin.site.register(OntologyTerm)
admin.site.register(MappingSuggestion)
admin.site.register(Comment)
admin.site.register(Review)
