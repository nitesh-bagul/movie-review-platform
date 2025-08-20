from django.urls import path,include
from movies.api.views import (GenreViewSet,PlatformViewSet,LanguageViewSet,
                              PersonViewSet,PersonRolaViewSet,MovieViewSet,
                              WebShowListView,WebShowDetailView,WebSeasonListView,
                              WebSeasonDetailView,WebShowEpisodeListView,
                              WebShowEpisodeDetailView,WebShowReviewView,
                              EpisodeReviewView,SeasonReviewView,
                              ReviewViewSet)
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
router.register(r'review',ReviewViewSet,basename='reviews')


urlpatterns = [
    path('',include(router.urls)),
    path('webshow/',WebShowListView.as_view(),name='web-show'),
    path('webshow/<int:pk>/',WebShowDetailView.as_view(),name='movie-detail'),
    path('webshow/<int:pk>/seasons/',WebSeasonListView.as_view()),
    path('seasons/<int:pk>/',WebSeasonDetailView.as_view()),
    path('season/<int:pk>/episodes/',WebShowEpisodeListView.as_view()),
    path('episodes/<int:pk>/',WebShowEpisodeDetailView.as_view()),
    path('webshow/<int:pk>/review/',WebShowReviewView.as_view()),
    path('season/<int:pk>/review/',SeasonReviewView.as_view()),
    path('episode/<int:pk>/review/',EpisodeReviewView.as_view()),
]