
from django.contrib import admin
from django.urls import path,include
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls'), name='api-root'),
] + debug_toolbar_urls()
