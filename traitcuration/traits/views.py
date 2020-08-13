import json
import requests
import gspread
from datetime import datetime
from github import Github

from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction

from .utils import get_status_dict, get_user_info, parse_request_body, get_initial_issue_body
from .models import Trait, Mapping, OntologyTerm, User, Status, Review, Comment
from .datasources import dummy, zooma
from .tasks import get_zooma_suggestions, get_clinvar_data, get_clinvar_data_and_suggestions, get_ols_status
from .forms import NewTermForm, GitHubSubmissionForm


def browse(request):
    request.session['github_access_token'] = None
    traits = Trait.objects.all()
    status_dict = get_status_dict(traits)
    context = {"traits": traits, "status_dict": status_dict}
    return render(request, 'traits/browse.html', context)


def trait_detail(request, pk):
    trait = get_object_or_404(Trait, pk=pk)
    reviewer_emails = list()
    if trait.current_mapping is not None:
        for review in trait.current_mapping.review_set.all():
            reviewer_emails.append(review.reviewer.email)
    status_dict = get_status_dict()
    history_events = list()
    comments = trait.comment_set.all()
    for comment in comments:
        history_events.append({'type': 'comment', 'date': comment.date, 'content': comment})
    mappings = trait.mapping_set.all()
    for mapping in mappings:
        history_events.append({'type': 'mapping', 'date': mapping.timestamp_mapped, 'content': mapping})
        reviews = mapping.review_set.all()
        for review in reviews:
            history_events.append({'type': 'review', 'date': review.timestamp, 'content': review})
    new_term_form = NewTermForm()
    context = {"trait": trait, "status_dict": status_dict,
               "new_term_form": new_term_form, "reviewer_emails": reviewer_emails, "history_events": history_events}
    return render(request, 'traits/trait_detail.html', context)


@transaction.atomic
def comment(request, pk):
    if request.method == 'GET':
        return redirect(reverse('trait_detail', args=[pk]))
    if request.user == "AnonymousUser":
        return HttpResponse('Unauthorized', status=401)
    request_body = parse_request_body(request)
    comment_body = request_body['comment_body']
    user_info = get_user_info(request)
    trait = get_object_or_404(Trait, pk=pk)
    user = get_object_or_404(User, email=user_info['email'])
    comment = Comment(trait_id=trait, author=user, body=comment_body)
    comment.save()
    return redirect(reverse('trait_detail', args=[pk]))


@transaction.atomic
def update_mapping(request, pk):
    if request.method == 'GET':
        return redirect(reverse('trait_detail', args=[pk]))
    if request.user == "AnonymousUser":
        return HttpResponse('Unauthorized', status=401)
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
    if request.user == "AnonymousUser":
        return HttpResponse('Unauthorized', status=401)
    trait = get_object_or_404(Trait, pk=pk)
    user_info = get_user_info(request)
    user = get_object_or_404(User, email=user_info['email'])
    body = parse_request_body(request)
    term = None
    if "term_iri" in body:
        termIRI = body['term_iri']
        term = zooma.create_local_term(termIRI)
        zooma.create_mapping_suggestion(trait, term, user_email=user_info["email"])
    else:
        term_label = body['label']
        term_description = body['description']
        term_cross_refs = body['cross_refs']
        term = OntologyTerm(label=term_label, description=term_description,
                            cross_refs=term_cross_refs, status=Status.NEEDS_CREATION)
        term.save()
        zooma.create_mapping_suggestion(trait, term, user_email=user_info["email"])
    mapping = Mapping(trait_id=trait, term_id=term, curator=user, is_reviewed=False)
    mapping.save()
    trait.current_mapping = mapping
    trait.save()
    return redirect(reverse('trait_detail', args=[pk]))


def review(request, pk):
    if request.method == 'GET':
        return redirect(reverse('trait_detail', args=[pk]))
    if request.user == "AnonymousUser":
        return HttpResponse('Unauthorized', status=401)
    user_info = get_user_info(request)
    user = get_object_or_404(User, email=user_info['email'])
    mapping = Trait.objects.get(pk=pk).current_mapping
    if mapping is None:
        return redirect(reverse('trait_detail', args=[pk]))
    if mapping.curator.id == user.id:
        return redirect(reverse('trait_detail', args=[pk]))
    for review in mapping.review_set.all():
        if review.reviewer.id == user.id:
            return redirect(reverse('trait_detail', args=[pk]))
    Review(mapping_id=mapping, reviewer=user).save()
    return redirect(reverse('trait_detail', args=[pk]))


def github_callback(request):
    payload = {}
    payload['client_id'] = '328c5e48d8b20f2849bd'
    payload['client_secret'] = '594e44da561dbd9169d57796de9c1cfa6a462f71'
    payload['code'] = request.GET['code']
    headers = {}
    headers['Accept'] = 'application/json'
    result = requests.post('https://github.com/login/oauth/access_token', data=payload, headers=headers)
    request.session['github_access_token'] = result.json()['access_token']
    return redirect('post_issue')


def post_issue(request):
    # Parse the form data containing the GitHub issue information
    if request.session.get('github_request'):
        request_body = request.session.get('github_request')
        print('lul')
        print(request_body)
    else:
        request_body = parse_request_body(request)
        request.session['github_request'] = request_body

    issue_title = request_body['title']
    issue_body = request_body['body']

    # Authenticate the user in Google Sheets and in GitHub
    gc = gspread.oauth()

    if request.session.get('github_access_token') is None:
        params = {}
        params['client_id'] = '328c5e48d8b20f2849bd'
        params['scope'] = 'user,repo'
        return redirect("https://github.com/login/oauth/authorize?scope=user,repo&client_id=328c5e48d8b20f2849bd")
    access_token = request.session.get('github_access_token')
    print(access_token)
    g = Github(access_token)

    # Create the spreadsheet
    sh = gc.create(issue_title)
    needs_import_worksheet = sh.add_worksheet(title="Terms to import", rows="100", cols="20")
    sh.del_worksheet(sh.sheet1)
    needs_import_worksheet.update('A1', 'IRI of selected mapping')
    needs_import_worksheet.update('B1', 'Label of selected mapping')
    needs_import_worksheet.update('C1', 'ClinVar label')
    needs_import_worksheet.update('D1', 'ClinVar Freq')
    needs_import_worksheet.format("A1:D1", {
        "backgroundColor": {
            "red": 0.82,
            "green": 0.88,
            "blue": 0.89
        },
        "textFormat": {
            "bold": True
        }
    })
    needs_import_traits = Trait.objects.filter(status=Status.NEEDS_IMPORT)
    for index, trait in enumerate(needs_import_traits):
        row_index = 2 + index
        needs_import_worksheet.update_cell(row_index, 1, trait.current_mapping.term_id.iri)
        needs_import_worksheet.update_cell(row_index, 2, trait.current_mapping.term_id.label)
        needs_import_worksheet.update_cell(row_index, 3, trait.name)
        needs_import_worksheet.update_cell(row_index, 4, trait.number_of_source_records)
    needs_creation_worksheet = sh.add_worksheet(title="Terms to create", rows="100", cols="20")
    needs_creation_worksheet.update('A1', 'Suggested term label')
    needs_creation_worksheet.update('B1', 'Suggested term description')
    needs_creation_worksheet.update('C1', 'Suggested term x-refs')
    needs_creation_worksheet.update('D1', 'ClinVar label')
    needs_creation_worksheet.update('E1', 'ClinVar freq')
    needs_creation_worksheet.format("A1:E1", {
        "backgroundColor": {
            "red": 0.82,
            "green": 0.88,
            "blue": 0.89
        },
        "textFormat": {
            "bold": True
        }
    })
    needs_creation_traits = Trait.objects.filter(status=Status.NEEDS_CREATION)
    for index, trait in enumerate(needs_creation_traits):
        row_index = 2 + index
        needs_creation_worksheet.update_cell(row_index, 1, trait.current_mapping.term_id.label)
        needs_creation_worksheet.update_cell(row_index, 2, trait.current_mapping.term_id.description)
        needs_creation_worksheet.update_cell(row_index, 3, trait.current_mapping.term_id.cross_refs)
        needs_creation_worksheet.update_cell(row_index, 4, trait.name)
        needs_creation_worksheet.update_cell(row_index, 5, trait.number_of_source_records)

    # Create the GitHub issue
    issue_body = issue_body.replace("{speadsheet_url}", sh.url)
    repo = g.get_repo("joj0s/django-notes-app")
    repo.create_issue(title=issue_title, body=issue_body)

    return redirect('datasources')


def feedback(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    traits_for_feedback = Trait.objects.filter(status__in=[Status.NEEDS_IMPORT, Status.NEEDS_CREATION])
    traits_for_import_count = traits_for_feedback.filter(status=Status.NEEDS_IMPORT).count()
    traits_for_creation_count = traits_for_feedback.filter(status=Status.NEEDS_CREATION).count()
    github_form = GitHubSubmissionForm()
    now = datetime.now()
    github_form.fields['title'].initial = f"EVA-EFO import {now.month}/{now.year}"
    github_form.fields['body'].initial = get_initial_issue_body(traits_for_import_count, traits_for_creation_count)
    context = {"traits_for_feedback": traits_for_feedback, "traits_for_import_count": traits_for_import_count,
               "traits_for_creation_count": traits_for_creation_count, "github_form": github_form}
    return render(request, 'traits/feedback.html', context)


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


def ols_queries(request):
    get_ols_status.delay()
    return redirect('datasources')
