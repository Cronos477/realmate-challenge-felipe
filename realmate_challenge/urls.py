from django.urls import path, include
from rest_framework import routers
from django.contrib import admin

router = routers.DefaultRouter()

urlpatterns = [
    path('', include('api.urls')),
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]
