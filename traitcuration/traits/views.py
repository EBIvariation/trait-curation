
import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from django.http import HttpResponse

from .utils import get_status_dict
from .models import Trait, Mapping, OntologyTerm, User, Status
from .datasources import dummy
from .tasks import get_zooma_suggestions, get_clinvar_data, get_clinvar_data_and_suggestions


def browse(request):
    traits = Trait.objects.all()
    status_dict = get_status_dict(traits)
    context = {"traits": traits, "status_dict": status_dict}
    return render(request, 'traits/browse.html', context)


def trait_detail(request, pk):
    trait = get_object_or_404(Trait, pk=pk)
    status_dict = get_status_dict()
    context = {"trait": trait, "status_dict": status_dict}
    return render(request, 'traits/trait_detail.html', context)


def update_mapping(request, pk):
    # Parse request body parameters, expected a trait id
    request_body = json.loads(request.body.decode('utf-8'))
    term_id = request_body['term']
    term = get_object_or_404(OntologyTerm, pk=term_id)
    trait = get_object_or_404(Trait, pk=pk)
    user = get_object_or_404(User, username='/ user1 /')
    # If a mapping instance with the given trait and term already exists, then map the trait to that, and reset reviews
    if Mapping.objects.filter(trait_id=trait, term_id=term).exists():
        mapping = Mapping.objects.filter(trait_id=trait, term_id=term).first()
        mapping.curator = user
        mapping.is_reviewed = False
    else:
        mapping = Mapping(trait_id=trait, term_id=term, curator=user, is_reviewed=False)
    mapping.save()
    trait.current_mapping = mapping
    trait.status = Status.AWAITING_REVIEW
    trait.timestamp_updated = datetime.now()
    trait.save()
    return HttpResponse(json.dumps(model_to_dict(mapping)), content_type="application/json")


def datasources(request):
    return render(request, 'traits/datasources.html')


def all_data(request):
    dummy.import_dummy_data()
    get_clinvar_data_and_suggestions.delay()
    return redirect('datasources')


def clinvar_data(request):
    get_clinvar_data.delay()
    return redirect('browse')


def zooma_suggestions(request):
    get_zooma_suggestions.delay()
    return redirect('datasources')


def dummy_data(request):
    dummy.import_dummy_data()
    return redirect('datasources')
