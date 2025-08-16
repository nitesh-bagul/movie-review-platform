from django.urls import path
from movies.api.views import (GenreViewSet,PlatformViewSet,LanguageViewSet,
                              PersonViewSet,PersonRolaViewSet,MovieViewSet)
from rest_framework.routers import DefaultRouter
# urlpatterns = [
#     # path('genre/',GenreViewSet.as_view(),name='genre-view'),
   
# ]

router=DefaultRouter()
router.register(r'genres',GenreViewSet,basename='genre',)
router.register(r'platforms',PlatformViewSet,basename='platform')
router.register(r'languages',LanguageViewSet,basename='language')
router.register(r'people',PersonViewSet,basename='person')
router.register(r'peoplerole',PersonRolaViewSet,basename='person-role') 
router.register(r'movies',MovieViewSet,basename='movie') 

urlpatterns = router.urls