from django.urls import path

from .views import TraitList


urlpatterns = [
    path('traits/', TraitList.as_view(), name='traits'),
]
