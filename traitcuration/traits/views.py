import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.urls import reverse

from .utils import get_status_dict, get_user_info, parse_request_body
from .models import Trait, Mapping, OntologyTerm, User, Status
from .datasources import dummy, zooma
from .tasks import get_zooma_suggestions, get_clinvar_data, get_clinvar_data_and_suggestions
from .forms import NewTermForm


def browse(request):
    traits = Trait.objects.all()
    status_dict = get_status_dict(traits)
    context = {"traits": traits, "status_dict": status_dict}
    return render(request, 'traits/browse.html', context)


def trait_detail(request, pk):
    trait = get_object_or_404(Trait, pk=pk)
    status_dict = get_status_dict()
    new_term_form = NewTermForm()
    context = {"trait": trait, "status_dict": status_dict, "new_term_form": new_term_form}
    return render(request, 'traits/trait_detail.html', context)


def update_mapping(request, pk):
    # Parse request body parameters, expected a trait id
    request_body = parse_request_body(request)
    term_id = request_body['term']
    term = get_object_or_404(OntologyTerm, pk=term_id)
    trait = get_object_or_404(Trait, pk=pk)
    user_info = get_user_info(request)
    user = get_object_or_404(User, email=user_info['email'])
    # If a mapping instance with the given trait and term already exists, then map the trait to that, and reset reviews
    if Mapping.objects.filter(trait_id=trait, term_id=term).exists():
        mapping = Mapping.objects.filter(trait_id=trait, term_id=term).first()
        mapping.curator = user
        mapping.is_reviewed = False
        mapping.review_set.all().delete()
    else:
        mapping = Mapping(trait_id=trait, term_id=term, curator=user, is_reviewed=False)
    mapping.save()
    trait.current_mapping = mapping
    trait.status = Status.AWAITING_REVIEW
    trait.timestamp_updated = datetime.now()
    trait.save()
    return HttpResponse(json.dumps(model_to_dict(mapping)), content_type="application/json")


def add_mapping(request, pk):
    if request.method == 'GET':
        return redirect(reverse('trait_detail', args=[pk]))
    trait = get_object_or_404(Trait, pk=pk)
    username = '/ user1 /'
    body = parse_request_body(request)
    term = None
    if "term_iri" in body:
        termIRI = body['term_iri']
        term = zooma.create_local_term(termIRI)
        zooma.create_mapping_suggestion(trait, term, username)
    else:
        term_label = body['label']
        term_description = body['description']
        term_cross_refs = body['cross_refs']
        term = OntologyTerm(label=term_label, description=term_description,
                            cross_refs=term_cross_refs, status=Status.NEEDS_CREATION)
        term.save()
        zooma.create_mapping_suggestion(trait, term, username)
    mapping = Mapping(trait_id=trait, term_id=term, curator=User.objects.filter(
        username=username).first(), is_reviewed=False)
    mapping.save()
    trait.current_mapping = mapping
    trait.save()
    return redirect(reverse('trait_detail', args=[pk]))


def datasources(request):
    # The task_id session variable is used to track task progress via the progress bar in the datasources page
    request.session['task_id'] = request.session.get('task_id', 'None')
    return render(request, 'traits/datasources.html')


def all_data(request):
    dummy.import_dummy_data()
    get_clinvar_data_and_suggestions.delay()
    return redirect('datasources')


def clinvar_data(request):
    get_clinvar_data.delay()
    return redirect('datasources')


def zooma_suggestions(request):
    result = get_zooma_suggestions.delay()
    request.session['task_id'] = result.task_id
    return redirect('datasources')


def dummy_data(request):
    dummy.import_dummy_data()
    return redirect('datasources')
