from django.shortcuts import render, get_object_or_404
from .models import Trait


def browse(request):
    traits = Trait.objects.all()
    context = {"traits": traits}
    return render(request, 'traits/browse.html', context)


def trait_detail(request, pk):
    trait = get_object_or_404(Trait, pk=pk)
    context = {"trait": trait}
    return render(request, 'traits/trait_detail.html', context)
