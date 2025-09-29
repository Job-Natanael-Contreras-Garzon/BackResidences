from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('auth/', include('apps.authentication.urls')),
    # path('security/', include('apps.security.urls')),
    # path('residences/', include('apps.residences.urls')),
    # path('payments/', include('apps.payments.urls')),
    # path('common-areas/', include('apps.common_areas.urls')),
]