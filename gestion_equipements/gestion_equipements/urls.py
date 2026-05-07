from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion_utilisateurs.urls')),
    path('equipements/', include('equipements.urls')),
    path('contacts/', include('contacts.urls')),
    path('emprunts/', include('emprunt.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)