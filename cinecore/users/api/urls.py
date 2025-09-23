from django.urls import path
from users.api.views import registration_view



urlpatterns = [
    path('register/',registration_view,name='api_register'),
    
]
