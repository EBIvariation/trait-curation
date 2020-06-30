
from django.shortcuts import render, get_object_or_404, redirect

from .utils import get_status_dict
from .models import Trait
from .datasources import clinvar, zooma


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


def datasources(request):
    return render(request, 'traits/datasources.html')


def clinvar_data(request):
    try:
        clinvar.download_clinvar_data()
        traits_dict = clinvar.parse_trait_names_and_source_records()
        clinvar.store_data(traits_dict)
        return redirect('browse')
    except Exception as e:
        print(f"Error: {e}")


def zooma_suggestions(request):
    zooma.get_zooma_suggestions()
    return redirect('datasources')
