from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("api.urls")),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-aut/', views.obtain_auth_token)
]
