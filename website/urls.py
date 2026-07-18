from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pricing/", views.pricing, name="pricing"),
    path("resources/", views.resources, name="resources"),
    path("trainings/", views.trainings, name="trainings"),
    path("licensure/", views.licensure, name="licensure"),
]
