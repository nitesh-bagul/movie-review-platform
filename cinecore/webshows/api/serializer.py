from rest_framework.serializers import Serializer,ModelSerializer
from movies.models import (Genre,Platform,Language,PersonRole,
                           Person,Movie,MovieRole,Review,WebShow,
                           WebSeason,Episode,MovieTrivia,GalleryImage,
                           BoxOffice,Award,FanTheory,PollOption,Poll)
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from movies.api.serializer import (GenreSerializer,LanguageSerializer,PlatformSerializer,
                                   ReviewSerializer,ActorRoleSerializer,CrewRoleSerializer,
                                   )


#WebShow Serializer

class WebShowListSerializer(ModelSerializer):
    genres=GenreSerializer(many=True,read_only=True)
    class Meta:
        model=WebShow
        fields=['title','poster_image','seasons_count','genres','status']

class WebShowCreateUpdateSerializer(ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)
    languages = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all(), many=True)
    subtitles = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all(), many=True)
    streaming_platform = serializers.PrimaryKeyRelatedField(queryset=Platform.objects.all(), many=True)
    creator = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all(), many=True)
    class Meta:
        model=WebShow
        fields=['id','title','short_synopsis','full_synopsis','status',
                'trailer','poster_image','backdrop_image','seasons_count',
                'is_active','genres','languages','subtitles','streaming_platform',
                'creator']

class WebShowDetailSerializer(ModelSerializer):
    genres=GenreSerializer(many=True,read_only=True)
    languages=LanguageSerializer(many=True,read_only=True)
    subtitles=LanguageSerializer(many=True,read_only=True)
    streaming_platform=PlatformSerializer(many=True,read_only=True)
    creator=serializers.StringRelatedField(many=True,read_only=True)
    reviews=ReviewSerializer(many=True,read_only=True)
    cast=serializers.SerializerMethodField()
    director=serializers.SerializerMethodField()
    producer=serializers.SerializerMethodField()
    writer=serializers.SerializerMethodField()
    class Meta:
        model=WebShow
        fields=['title','genres','short_synopsis','full_synopsis','languages',
                'subtitles','poster_image','backdrop_image',
                'trailer','streaming_platform','cast','creator','reviews',
                'director','producer','writer']
        
    def get_cast(self,obj):
        role=obj.webshow_role.filter(role=MovieRole.ACTOR)
        return ActorRoleSerializer(role,many=True).data
    
    def get_director(self,obj):
        role=obj.webshow_role.filter(role=MovieRole.DIRECTOR)
        return CrewRoleSerializer(role,many=True).data
    
    def get_producer(self,obj):
        role=obj.webshow_role.filter(role=MovieRole.PRODUCER)
        return CrewRoleSerializer(role,many=True).data
    
    def get_writer(self,obj):
        role=obj.webshow_role.filter(role=MovieRole.WRITER)
        return CrewRoleSerializer(role,many=True).data

class WebSeasonListSerializer(ModelSerializer):
    webshow=WebShowListSerializer(read_only=True)
    class Meta:
        model=WebSeason
        fields=['id','webshow','season_number','poster_image']


class WebSeasonDetailSerializer(ModelSerializer):
    webshow=WebShowListSerializer(read_only=True)
    reviews=ReviewSerializer(many=True,read_only=True)
    class Meta:
        model=WebSeason
        fields=['id','webshow','season_number','poster_image',
                'description','total_episodes','release_date',
                'reviews']


class WebSeasonCreateUpdateSerializer(ModelSerializer):
    # webshow=serializers.PrimaryKeyRelatedField(queryset=WebShow.objects.all())
    class Meta:
        model=WebSeason
        fields=['id','season_number','description','poster_image','total_episodes',
                'release_date']

class WebSeasonEpisodeListSerializer(ModelSerializer):
    class Meta:
        model=Episode
        fields=['id','title','episode_number','release_date','thumbnail_img',
                'runtime']

class WebShowEpisodeDetailSerializer(ModelSerializer):
    reviews=ReviewSerializer(many=True,read_only=True)
    season=WebSeasonListSerializer(read_only=True)
    class Meta:
        model=Episode
        fields=['id','season','title','episode_number','description','release_date','thumbnail_img',
                'runtime','reviews']


class EpisodeCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model=Episode
        fields=['episode_number','title','description','release_date','thumbnail_img',
                'runtime']


