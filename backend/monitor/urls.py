from django.urls import path
from . import views

urlpatterns = [
    path("simulate/", views.SimulateView.as_view()),
    path("analyze/", views.AnalyzeView.as_view()),
    path("results/", views.ResultsView.as_view()),
    path("health/", views.HealthView.as_view()),
]
