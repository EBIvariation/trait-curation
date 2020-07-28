from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from computedfields.models import ComputedFieldsModel, computed

from .managers import CustomUserManager


class Status(models.TextChoices):
    CURRENT = 'current'
    UNMAPPED = 'unmapped'
    OBSOLETE = 'obsolete'
    DELETED = 'deleted'
    NEEDS_IMPORT = 'needs_import'
    AWAITING_IMPORT = 'awaiting_import'
    NEEDS_CREATION = 'needs_creation'
    AWAITING_CREATION = 'awaiting_creation'
    AWAITING_REVIEW = 'awaiting_review'

    @classmethod
    def trait_choices(cls):
        return tuple((i.name, i.value) for i in cls)

    @classmethod
    def term_choices(cls):
        choices = list()
        for i in cls:
            if i.name != 'UNMAPPED' and i.name != 'AWAITING_REVIEW':
                choices.append((i.name, i.value))
        return tuple(choices)


class Trait(ComputedFieldsModel):
    name = models.CharField(max_length=200)
    current_mapping = models.ForeignKey('Mapping', on_delete=models.SET_NULL, null=True, blank=True)
    number_of_source_records = models.IntegerField(blank=True, null=True)
    timestamp_added = models.DateTimeField(auto_now=True)
    timestamp_updated = models.DateTimeField(auto_now_add=True)

    @computed(models.CharField(max_length=30, choices=Status.trait_choices()), depends=[
        ['current_mapping', ['is_reviewed']],
        ['current_mapping.term_id', ['status']]
    ])
    def status(self):
        if not self.current_mapping:
            return Status.UNMAPPED
        return self.current_mapping.term_id.status if self.current_mapping.is_reviewed else Status.AWAITING_REVIEW

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class OntologyTerm(models.Model):
    curie = models.CharField(max_length=50, blank=True, null=True, unique=True)
    iri = models.URLField(null=True, blank=True, unique=True)
    label = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=Status.term_choices())
    description = models.TextField(blank=True, null=True)
    cross_refs = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.curie} - {self.label}"


class Mapping(ComputedFieldsModel):
    trait_id = models.ForeignKey(Trait, on_delete=models.PROTECT)
    term_id = models.ForeignKey(OntologyTerm, on_delete=models.PROTECT)
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp_mapped = models.DateTimeField(auto_now=True)

    @computed(models.BooleanField(), depends=[
        ['review_set', []],
    ])
    def is_reviewed(self):
        return self.review_set.count() >= 2

    def __str__(self):
        return f"{self.trait_id} - {self.term_id}"

    class Meta:
        unique_together = ('trait_id', 'term_id',)


class MappingSuggestion(models.Model):
    trait_id = models.ForeignKey(Trait, on_delete=models.PROTECT)
    term_id = models.ForeignKey(OntologyTerm, on_delete=models.PROTECT)
    made_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trait: {self.trait_id} | Term: {self.term_id}"

    class Meta:
        unique_together = ('trait_id', 'term_id',)


class Review(models.Model):
    mapping_id = models.ForeignKey(Mapping, on_delete=models.PROTECT)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.mapping_id} by {self.reviewer}"


class Comment(models.Model):
    trait_id = models.ForeignKey(Trait, on_delete=models.PROTECT)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now=True)
    body = models.TextField()

    def __str__(self):
        return f"By {self.author} on {self.date}"
