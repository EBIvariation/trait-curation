from . import views
from django.urls import path

urlpatterns = [
    path('', views.browse, name="browse"),
    path('<int:pk>/', views.trait_detail, name="trait_detail"),
    path('datasources/', views.datasources, name="datasources"),
<<<<<<< HEAD
    path('datasources/all', views.all_data, name="all_data"),
    path('datasources/dummy', views.dummy_data, name="dummy_data"),
    path('datasources/zooma', views.zooma_suggestions, name="zooma_suggestions"),
=======
    path('datasources/zooma', views.zooma_suggestions, name="zooma_suggestions"),
    path('datasources/dummy', views.dummy_data, name="dummy_data"),
>>>>>>> 7acb96b8e7b79e355220a06db335c555ee389d41
    path('datasources/clinvar', views.clinvar_data, name="clinvar_data"),
]
