from rest_framework.serializers import Serializer,ModelSerializer
from movies.models import (Genre,Platform,Language,PersonRole,
                           Person,Movie,MovieRole,Review,WebShow)
from rest_framework import serializers
class GenreSerializer(ModelSerializer):
    class Meta:
        model=Genre
        fields=['id','name']

class ReviewSerializer(ModelSerializer):
    user=serializers.StringRelatedField()
    class Meta:
        model=Review
        fields=['id', 'user', 'review_text', 'rating', 'is_critic', 'timestamp']

class PlatformSerializer(ModelSerializer):
    class Meta:
        model=Platform
        fields=['id', 'name', 'logo_image', 'website_link']


class LanguageSerializer(ModelSerializer):
    class Meta:
        model=Language
        fields=['id','name']


class PersonalRoleSerializer(ModelSerializer):
    movie=serializers.StringRelatedField()
    webshow=serializers.StringRelatedField()
    person=serializers.StringRelatedField()
    class Meta:
        model=PersonRole
        fields=['id','person','role', 'character_name','movie','webshow']

class ActorRoleSerializer(ModelSerializer):
    person=serializers.StringRelatedField()
    class Meta:
        model=PersonRole
        fields=['id','person','role', 'character_name']

class CrewRoleSerializer(serializers.ModelSerializer):
    person = serializers.StringRelatedField()

    class Meta:
        model = PersonRole
        fields = [ 'id','person', 'role']

class PersonSerializer(ModelSerializer):
    person_role=PersonalRoleSerializer(many=True,read_only=True) 
    class Meta:
        model=Person
        fields=['id', 'name', 'profile_pic', 'bio', 'birth_date', 'person_role']


class MovieListSerializer(ModelSerializer):
    genres=serializers.StringRelatedField(many=True,read_only=True)
    class Meta:
        model=Movie
        fields=['id','title','poster_image','release_date','genres']

class MovieDetailSerializer(ModelSerializer):
    genres=serializers.StringRelatedField(many=True,read_only=True)
    cast = serializers.SerializerMethodField()
    directors = serializers.SerializerMethodField()
    languages=LanguageSerializer(many=True,read_only=True)
    streaming_platform=PlatformSerializer(many=True,read_only=True)
    subtitles=serializers.SerializerMethodField()
    reviews=ReviewSerializer(many=True,read_only=True)
    # writers = serializers.SerializerMethodField()
    # producers = serializers.SerializerMethodField()
  
    class Meta:
        model=Movie
        fields=['id','title','poster_image','release_date','genres',
                'short_synopsis','full_synopsis','cast', 'directors',
                'languages','streaming_platform','trailer','runtime',
                'subtitles','reviews'
                ]
    def get_cast(self,obj):
        role=obj.movie_role.filter(role=MovieRole.ACTOR)
        return ActorRoleSerializer(role,many=True).data
    
    def get_directors(self,obj):
        role=obj.movie_role.filter(role=MovieRole.DIRECTOR)
        return CrewRoleSerializer(role,many=True).data  
    
    def get_subtitles(self,obj):
        subtitle=obj.subtitles.all()
        return LanguageSerializer(subtitle,many=True).data


class ReviewSerializer(ModelSerializer):
    user=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=Review
        fields=['user','review_text','rating','is_critic','timestamp']


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
             
