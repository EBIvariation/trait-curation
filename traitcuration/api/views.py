from rest_framework import viewsets, permissions, generics

from .serializers import OntologyTermSerializer, TraitSerializer, MappingSerializer, UserSerializer
from traitcuration.traits.models import OntologyTerm, Trait, Mapping, User


class TraitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Trait.objects.all()
    serializer_class = TraitSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class TraitList(generics.ListAPIView):
    serializer_class = TraitSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Trait.objects.all()
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset


class OntologyTermList(generics.ListAPIView):
    serializer_class = OntologyTermSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = OntologyTerm.objects.all()
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset

# class OntologyTermViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     def get_queryset(self):
#         """
#         Optionally restricts the returned purchases to a given user,
#         by filtering against a `username` query parameter in the URL.
#         """
#         queryset = Purchase.objects.all()
#         username = self.request.query_params.get('username', None)
#         if username is not None:
#             queryset = queryset.filter(purchaser__username=username)
#         return queryset

#     queryset = OntologyTerm.objects.all()
#     serializer_class = OntologyTermSerializer
#     permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class MappingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Mapping.objects.all()
    serializer_class = MappingSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
