from django.shortcuts import render


def browse(request):
    return render(request, 'traits/browse.html')


def trait_detail(request, pk):
    return render(request, 'traits/trait_detail.html')
