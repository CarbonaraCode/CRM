from django.contrib import admin
from django.urls import path

urlpatterns = [
    # Rotta per il pannello di amministrazione
    path('admin/', admin.site.urls),
]
