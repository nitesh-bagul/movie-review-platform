from rest_framework.views import APIView
from movies.models import (Genre,Platform,Language,Person,PersonRole,
                           Movie)
from movies.api.serializer import (GenreSerializer,PlatformSerializer,
                                   LanguageSerializer,PersonSerializer,
                                   PersonalRoleSerializer,MovieListSerializer,
                                   MovieDetailSerializer)
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

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
        return MovieDetailSerializer
       


