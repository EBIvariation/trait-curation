import json

import gspread
from github import Github
from allauth.socialaccount.models import SocialAccount

from .models import Status, Trait, OntologyTerm


def get_status_dict(traits=[]):
    status_dict = {
        "all": {"count": len(traits), "class": "primary"},
        "awaiting_review": {"count": 0, "class": "warning"},
        "awaiting_creation": {"count": 0, "class": "warning"},
        "needs_creation": {"count": 0, "class": "warning"},
        "awaiting_import": {"count": 0, "class": "warning"},
        "needs_import": {"count": 0, "class": "warning"},
        "unmapped": {"count": 0, "class": "danger"},
        "obsolete": {"count": 0, "class": "danger"},
        "deleted": {"count": 0, "class": "danger"},
        "current": {"count": 0, "class": "success"},
    }
    for trait in traits:
        status_dict[trait.status]["count"] += 1
    return status_dict


def get_user_info(request):
    user_info = SocialAccount.objects.get(user=request.user).extra_data
    return user_info


def parse_request_body(request):
    """
    Accepts a Django request body as an argument and returns a dict object with the request body.
    """
    body = request.POST.dict() if request.POST.dict() else json.loads(request.body.decode('utf-8'))
    return body


def create_spreadsheet_and_issue(github_access_token, issue_info):
    gc = gspread.oauth()

    github = Github(github_access_token)

    # Create the spreadsheet
    sheet = gc.create(issue_info['title'])
    needs_import_worksheet = sheet.add_worksheet(title="Terms to import", rows="100", cols="20")
    sheet.del_worksheet(sheet.sheet1)
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
    needs_creation_worksheet = sheet.add_worksheet(title="Terms to create", rows="100", cols="20")
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

    gc.insert_permission(sheet.id, None, perm_type='anyone', role='writer')
    repo = github.get_repo(issue_info['repo'])
    # Create the GitHub issue
    issue_body = issue_info['body'].replace("{speadsheet_url}", sheet.url)
    repo = github.get_repo(issue_info['repo'])
    issue = repo.create_issue(title=issue_info['title'], body=issue_body)

    needs_import_terms = OntologyTerm.objects.filter(status=Status.NEEDS_IMPORT)
    for term in needs_import_terms:
        term.status = Status.AWAITING_IMPORT
        term.save()
    needs_creation_terms = OntologyTerm.objects.filter(status=Status.NEEDS_CREATION)
    for term in needs_creation_terms:
        term.status = Status.AWAITING_CREATION
        term.save()

    return f"https://github.com/{issue_info['repo']}/issues/{issue.number}"


def get_initial_issue_body(traits_for_import_count, traits_for_creation_count):
    return (f"This release consists of {traits_for_import_count} potential entries to import and "
            f"{traits_for_creation_count} potential terms to create."
            "\n\nSpreadsheet: {speadsheet_url}")
