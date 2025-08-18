from django.urls import path,include
from movies.api.views import (GenreViewSet,PlatformViewSet,LanguageViewSet,
                              PersonViewSet,PersonRolaViewSet,MovieViewSet,
                              WebShowListView,WebShowDetailView)
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

urlpatterns = [
    path('',include(router.urls)),
    path('webshow/',WebShowListView.as_view(),name='web-show'),
    path('webshow/<int:pk>/',WebShowDetailView.as_view(),name='movie-detail')
]