from django.urls import include, path

urlpatterns = [
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
