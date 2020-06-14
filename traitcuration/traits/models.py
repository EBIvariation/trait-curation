from django.db import models


class Trait(models.Model):
    name = models.CharField(max_length=200)
    current_mapping = models.ForeignKey(
        'Mapping', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50)
    number_of_source_records = models.IntegerField(blank=True, null=True)
    timestamp_added = models.DateTimeField(auto_now=True)
    timestamp_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class OntologyTerm(models.Model):
    curie = models.CharField(max_length=50, blank=True, null=True, unique=True)
    uri = models.URLField(null=True, blank=True, unique=True)
    label = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    cross_refs = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.curie} | {self.label}"


class Mapping(models.Model):
    trait_id = models.ForeignKey(Trait, on_delete=models.PROTECT)
    term_id = models.ForeignKey(OntologyTerm, on_delete=models.PROTECT)
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_reviewed = models.BooleanField()
    timestamp_mapped = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trait_id} - {self.term_id}"


class MappingSuggestion(models.Model):
    trait_id = models.ForeignKey(Trait, on_delete=models.PROTECT)
    term_id = models.ForeignKey(OntologyTerm, on_delete=models.PROTECT)
    made_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trait_id} | {self.term_id}"


class Comment(models.Model):
    trait_id = models.ForeignKey(Trait, on_delete=models.PROTECT)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now=True)
    body = models.TextField()

    def __str__(self):
        return f"By {self.author} on {self.date}"
