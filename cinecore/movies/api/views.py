from rest_framework.views import APIView
from movies.models import (Genre,Platform,Language,Person,PersonRole,
                           Movie,Review,WebShow,WebSeason,Episode,MovieRole)
from movies.api.serializer import (GenreSerializer,PlatformSerializer,
                                   LanguageSerializer,PersonSerializer,
                                   PersonalRoleSerializer,MovieListSerializer,
                                   MovieDetailSerializer,ReviewSerializer,
                                   WebShowListSerializer,WebShowDetailSerializer,
                                   WebShowCreateUpdateSerializer,WebSeasonListSerializer,
                                   WebSeasonDetailSerializer,WebSeasonCreateUpdateSerializer,
                                   WebSeasonEpisodeListSerializer,WebShowEpisodeDetailSerializer,
                                   EpisodeCreateUpdateSerializer,MovieUpdateSerializer,
                                   MovieCreateSerializer,CrewRoleSerializer,
                                   )
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

#generic view
from rest_framework.generics import (ListAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView)

# class GenreViewSet(APIView):
#     def get(self,request):
#         genre=Genre.objects.all()
#         serializer=GenreSerializer(genre,many=True)
#         return Response(serializer.data)

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Genre.objects.all()
    serializer_class=GenreSerializer
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_articles = self.queryset.order_by('-id')[:2]
        serializer = self.get_serializer(recent_articles, many=True)
        return Response(serializer.data)

class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Platform.objects.all()
    serializer_class=PlatformSerializer

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Language.objects.all()
    serializer_class=LanguageSerializer
    
class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer

class PersonRolaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=PersonRole.objects.all()
    serializer_class=PersonalRoleSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset=Movie.objects.prefetch_related(
        'genres', 'languages', 'subtitles', 'streaming_platform',
        'movie_role__person', 'reviews'
    )
    
    def get_serializer_class(self):
        if self.action=='list':
            return MovieListSerializer
        elif self.action=='create':
            return MovieCreateSerializer
        elif self.action=='retrieve':
            return MovieDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return MovieUpdateSerializer
        
        elif self.action == 'reviews':
            return ReviewSerializer
        return MovieDetailSerializer
    
    @action(detail=True,methods=['GET','POST'])
    def reviews(self,request, *args, **kwargs):
        movie=self.get_object()
        if request.method=='GET':
            queryset=movie.reviews.all()
            serializer=ReviewSerializer(queryset, many=True)
            return Response(serializer.data)
        
        elif request.method=='POST':
            serializer=ReviewSerializer(data=request.data)
            review_user=request.user
            review_queryset=movie.reviews.filter(user=review_user)
            if review_queryset.exists():
                raise ValidationError("You have already reviewed")  
            
            serializer.is_valid(raise_exception=True)
            serializer.save(content_object=movie,user=review_user)
            return Response(serializer.data)
    @action(detail=True,methods=['GET']) 
    def cast(self,request, *args, **kwargs):
        movie=self.get_object()
        queryset=movie.movie_role.all().filter(role=MovieRole.ACTOR) 
        serializer=PersonalRoleSerializer(queryset,many=True)
        return Response(serializer.data)
    @action(detail=True,methods=['GET']) 
    def crew(self,request,*args,**kwargs):
        movie=self.get_object()
        queryset=movie.movie_role.all().filter(role__in=[MovieRole.DIRECTOR,
                MovieRole.WRITER,MovieRole.PRODUCER,MovieRole.MUSIC_DIRECTOR,
                MovieRole.CINEMATOGRAPHER])
        serializer=CrewRoleSerializer(queryset,many=True)
        return Response(serializer.data) 
    @action(detail=True,methods=['GET'])
    def languages(self,request,*args,**kwargs):
        movie=self.get_object()
        queryset=movie.languages.all()
        serializer=LanguageSerializer(queryset,many=True)
        return Response(serializer.data) 
    @action(detail=True,methods=['GET'])
    def platforms(self,request,*args,**kwargs):
        movie=self.get_object()
        queryset=movie.streaming_platform.all()
        serializer=PlatformSerializer(queryset,many=True)
        return Response(serializer.data) 
    @action(detail=True,methods=['GET'])
    def subtitles(self,request,*args,**kwargs):
        movie=self.get_object()
        queryset=movie.subtitles.all()
        serializer=LanguageSerializer(queryset,many=True)
        return Response(serializer.data) 
    @action(detail=True,methods=['GET'])
    def trailers(self,request,*args,**kwargs):
        movie=self.get_object()
        print(movie.trailer)
        return Response({"trailer": movie.trailer}) 
        

class MovieCastView(viewsets.ModelViewSet):
    queryset=Movie.objects.all()
    serializer_class=MovieListSerializer
    
    @action(detail=True,methods=['GET'])
    def cast(self,request, *args, **kwargs):
        movie=self.get_object()
        queryset=movie.movie_role.all() 
        serializer=PersonalRoleSerializer(queryset,many=True)
        return Response(serializer.data)
            
    
    
# WebShow views

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

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user').all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


