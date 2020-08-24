from rest_framework import generics

from .serializers import TraitSerializer
from traitcuration.traits.models import Trait


class TraitList(generics.ListAPIView):
    http_method_names = ['get']
    serializer_class = TraitSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Trait.objects.all().order_by('-number_of_source_records')
        status = self.request.query_params.get('status', None)
        name = self.request.query_params.get('name', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        return queryset
