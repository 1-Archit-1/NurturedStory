from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
]

# Serve uploaded media files via Django.
# WhiteNoise only handles static files baked into the image — media files are
# user-uploaded at runtime so Django serves them directly here.
# Note: we register serve() directly rather than using static() because
# django.conf.urls.static.static() silently no-ops when DEBUG=False.
# This is fine for low-traffic admin uploads (therapist photo, resource files).
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
