from django.urls import path
from webshows.api.views import (WebShowListView,WebShowDetailView,WebSeasonListView,
                              WebSeasonDetailView,WebShowEpisodeListView,
                              WebShowEpisodeDetailView,WebShowReviewView,
                              EpisodeReviewView,SeasonReviewView)

urlpatterns = [
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
