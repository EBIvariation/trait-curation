from django.urls import include, path
from rest_framework import routers

from .views import OntologyTermList, MappingViewSet, UserViewSet, TraitList

router = routers.DefaultRouter()
# router.register(r'traits', TraitViewSet)
router.register(r'mappings', MappingViewSet)
router.register(r'users', UserViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('terms/', OntologyTermList.as_view(), name='terms'),
    path('traits/', TraitList.as_view(), name='traits'),
    path('', include(router.urls)),
]
