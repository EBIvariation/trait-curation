from django.shortcuts import render, get_object_or_404
from .utils import get_status_dict
from .models import Trait


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
