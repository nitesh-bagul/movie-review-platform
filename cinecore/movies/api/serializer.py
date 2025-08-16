from rest_framework.serializers import Serializer,ModelSerializer
from movies.models import (Genre,Platform,Language,PersonRole,
                           Person,Movie,MovieRole,Review)
from rest_framework import serializers
class GenreSerializer(ModelSerializer):
    class Meta:
        model=Genre
        fields=['id', 'name']

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
        fields=['name']


class PersonalRoleSerializer(ModelSerializer):
    movie=serializers.StringRelatedField()
    webshow=serializers.StringRelatedField()
    person=serializers.StringRelatedField()
    class Meta:
        model=PersonRole
        fields=['person','role', 'character_name','movie','webshow']

class ActorRoleSerializer(ModelSerializer):
    person=serializers.StringRelatedField()
    class Meta:
        model=PersonRole
        fields=['person','role', 'character_name']

class CrewRoleSerializer(serializers.ModelSerializer):
    person = serializers.StringRelatedField()

    class Meta:
        model = PersonRole
        fields = [ 'person', 'role']

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