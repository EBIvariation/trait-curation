from django.shortcuts import render, get_object_or_404
from .models import Trait


def browse(request):
    traits = Trait.objects.all()
    status_dict = get_status_dict(traits)
    context = {"traits": traits, "status_dict": status_dict}
    return render(request, 'traits/browse.html', context)


def trait_detail(request, pk):
    trait = get_object_or_404(Trait, pk=pk)
    context = {"trait": trait}
    return render(request, 'traits/trait_detail.html', context)


def get_status_dict(traits):
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
