from django.shortcuts import render
from .models import Trait


def browse(request):
    traits = Trait.objects.all()
    context = {"traits": traits}
    return render(request, 'traits/browse.html', context)


def trait_detail(request, pk):
    return render(request, 'traits/trait_detail.html')
