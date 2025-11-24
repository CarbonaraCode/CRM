from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Rotta per il pannello di amministrazione
    path('admin/', admin.site.urls),
    path('api/sales/', include('sales.urls')),
]
