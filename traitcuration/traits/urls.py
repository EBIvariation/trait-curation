from . import views
from django.urls import path

urlpatterns = [
    path('', views.browse, name="browse"),
    path('<int:pk>/', views.trait_detail, name="trait_detail"),
    path('datasources/', views.datasources, name="datasources"),
    path('datasources/zooma', views.zooma_suggestions, name="zooma_suggestions"),
    path('datasources/dummy', views.dummy_data, name="dummy_data"),
    path('datasources/clinvar', views.clinvar_data, name="clinvar_data"),
]
