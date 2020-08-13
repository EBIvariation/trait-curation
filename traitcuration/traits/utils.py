import json

from allauth.socialaccount.models import SocialAccount


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


def get_initial_issue_body(traits_for_import_count, traits_for_creation_count):
    return (f"This release consists of {traits_for_import_count} potential entries to import and"
            f"{traits_for_creation_count} potential terms to create."
            "\n\nSpreadsheet: {speadsheet_url}")
