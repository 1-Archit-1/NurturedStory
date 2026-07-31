from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pricing/", views.pricing, name="pricing"),
    path("resources/", views.resources, name="resources"),
    path("trainings/", views.trainings, name="trainings"),
    path("licensure/", views.licensure, name="licensure"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("healthz", views.health_check, name="health_check"),
]
