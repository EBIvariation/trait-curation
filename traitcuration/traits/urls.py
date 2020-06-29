from . import views
from django.urls import path

urlpatterns = [
    path('', views.browse, name="browse"),
    path('<int:pk>/', views.trait_detail, name="trait_detail"),
    path('datasources/', views.datasources, name="datasources"),
    path('clinvar/', views.clinvar_data, name="clinvar_data"),
    path('zooma/', views.zooma_suggestions, name="zooma_suggestions")
]
