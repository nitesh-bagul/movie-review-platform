from rest_framework.views import APIView
from movies.models import (Genre,Platform,Language,Person,PersonRole,
                           Movie,Review,WebShow)
from movies.api.serializer import (GenreSerializer,PlatformSerializer,
                                   LanguageSerializer,PersonSerializer,
                                   PersonalRoleSerializer,MovieListSerializer,
                                   MovieDetailSerializer,ReviewSerializer,
                                   WebShowListSerializer,WebShowDetailSerializer,
                                   WebShowCreateUpdateSerializer)
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

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
        elif self.action=='retrieve':
            return MovieDetailSerializer
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
 
        


