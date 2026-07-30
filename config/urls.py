from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
]

# Serve uploaded media files via Django.
# WhiteNoise only handles static files baked into the image — media files are
# user-uploaded at runtime so Django serves them directly here.
# This is fine for low-traffic admin uploads (therapist photo, etc.)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
