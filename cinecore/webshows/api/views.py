# WebShow views
from movies.models import *
from webshows.api.serializer import (WebShowListSerializer,WebShowCreateUpdateSerializer,
                                     WebShowDetailSerializer,WebSeasonListSerializer,
                                     WebSeasonCreateUpdateSerializer,WebSeasonDetailSerializer,
                                     WebSeasonEpisodeListSerializer,EpisodeCreateUpdateSerializer,
                                     WebShowEpisodeDetailSerializer,ReviewSerializer)
from django.contrib.contenttypes.models import ContentType
from rest_framework.generics import (ListAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                    ListCreateAPIView)

class WebShowListView(ListCreateAPIView):
    queryset=WebShow.objects.all()
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WebShowListSerializer
        elif self.request.method == 'POST':
            return WebShowCreateUpdateSerializer
        return WebShowListSerializer    
    
 


class WebShowDetailView(RetrieveUpdateDestroyAPIView):
    queryset=WebShow.objects.prefetch_related(
        'genres', 'languages', 'subtitles', 'streaming_platform',
        'creator',
        'webshow_role__person',
        'seasons',
        'reviews'
    )
    def get_serializer_class(self):
        if self.request.method in ['PUT','PATCH']:
            return WebShowCreateUpdateSerializer
        return WebShowDetailSerializer
 
        


class WebSeasonListView (ListCreateAPIView):
    queryset= WebSeason.objects.select_related('webshow').all()
    
    def get_serializer_class(self):
        if self.request.method=='GET':
            return WebSeasonListSerializer
        elif self.request.method=='POST':
            return WebSeasonCreateUpdateSerializer
        return WebSeasonListSerializer
    
    def get_queryset(self):
        pk = self.kwargs.get('pk') 
        print(pk)
        return WebSeason.objects.filter(webshow_id=pk)
    
    def perform_create(self, serializer):
        pk=self.kwargs.get('pk')
        webshow=WebShow.objects.get(pk=pk)
        print(webshow)
        serializer.save(webshow=webshow)
    
 


class WebSeasonDetailView(RetrieveUpdateDestroyAPIView):
    queryset=WebSeason.objects.select_related('webshow').all()
    # serializer_class=WebSeasonDetailSerializer   
    
    def get_serializer_class(self):
        if self.request.method in ['PUT','PATCH']:
            return WebSeasonCreateUpdateSerializer
        return WebSeasonDetailSerializer
 
class WebShowEpisodeListView(ListCreateAPIView):
    queryset=Episode.objects.select_related('season').all()
    
    def get_queryset(self):
        pk=self.kwargs.get('pk')
        return Episode.objects.filter(season=pk)
    
    def perform_create(self, serializer):
        pk=self.kwargs.get('pk')
        print(pk)
        season=WebSeason.objects.get(id=pk)
        print(season)
        serializer.save(season=season)
    
    def get_serializer_class(self):
        if self.request.method=="GET":
            return WebSeasonEpisodeListSerializer
        elif self.request.method=='POST':
            return EpisodeCreateUpdateSerializer   
        return WebSeasonEpisodeListSerializer

class WebShowEpisodeDetailView(RetrieveUpdateDestroyAPIView):
    queryset=Episode.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['PUT','PATCH']:
            return EpisodeCreateUpdateSerializer
        return WebShowEpisodeDetailSerializer

class WebShowReviewView(ListAPIView):
    serializer_class=ReviewSerializer
    
    def get_queryset(self):
        webshow_pk = self.kwargs.get('pk')
        webshow_ct = ContentType.objects.get_for_model(WebShow)
        return Review.objects.filter(
            content_type=webshow_ct,
            object_id=webshow_pk
        )
        
# def get_queryset(self):
#         webshow_id = self.kwargs.get('pk')
#         return Review.objects.filter(
#             content_type__model='webshow',
#             object_id=webshow_id
#         )

class EpisodeReviewView(ListAPIView):
    serializer_class=ReviewSerializer
    def get_queryset(self):
        episode_id=self.kwargs.get('pk')
        episode_ct=ContentType.objects.get_for_model(Episode)
        return Review.objects.filter(
            content_type=episode_ct,
            object_id=episode_id
        )

class SeasonReviewView(ListAPIView):
    serializer_class=ReviewSerializer
    def get_queryset(self):
        season_id=self.kwargs.get('pk')
        season_ct=ContentType.objects.get_for_model(WebSeason)
        return Review.objects.filter(
            content_type=season_ct,
            object_id=season_id
        )