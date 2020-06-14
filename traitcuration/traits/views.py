from django.shortcuts import render, get_object_or_404
from .models import Trait


def browse(request):
    traits = Trait.objects.all()
    status_list = get_status_list(traits)
    context = {"traits": traits, "status_list": status_list}
    return render(request, 'traits/browse.html', context)


def trait_detail(request, pk):
    trait = get_object_or_404(Trait, pk=pk)
    context = {"trait": trait}
    return render(request, 'traits/trait_detail.html', context)


def get_status_list(traits):
    status_list = [
        {"status": "all", "count": len(traits), "class": "primary"},
        {"status": "awaiting_review", "count": 0, "class": "warning"},
        {"status": "awaiting_creation", "count": 0, "class": "warning"},
        {"status": "needs_creation", "count": 0, "class": "warning"},
        {"status": "awaiting_import", "count": 0, "class": "warning"},
        {"status": "needs_import", "count": 0, "class": "warning"},
        {"status": "unmapped", "count": 0, "class": "danger"},
        {"status": "obsolete", "count": 0, "class": "danger"},
        {"status": "deleted", "count": 0, "class": "danger"},
        {"status": "current", "count": 0, "class": "success"}
    ]
    for trait in traits:
        for status in status_list:
            if status['status'] == trait.status:
                status['count'] += 1
    return status_list
