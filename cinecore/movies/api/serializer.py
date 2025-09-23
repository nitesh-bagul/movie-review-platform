from rest_framework.serializers import Serializer,ModelSerializer
from movies.models import (Genre,Platform,Language,PersonRole,
                           Person,Movie,MovieRole,Review,MovieTrivia,
                           GalleryImage,BoxOffice,Award,FanTheory,
                           PollOption,Poll)

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.utils.timezone import localdate
from django.db.models.functions import TruncDate
class GenreSerializer(ModelSerializer):
    class Meta:
        model=Genre
        fields=['id','name']

class ReviewSerializer(ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)  # Show username or string representation of user
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.all(), write_only=True)
    object_id = serializers.IntegerField(write_only=True)
    likes_count = serializers.SerializerMethodField() 
    movie_title=serializers.SerializerMethodField()
     

    class Meta:
        model = Review
        fields = [
            'id', 'movie_title','review_user', 'review_text', 'rating', 'is_critic',
            'timestamp', 'content_type', 'object_id','likes_count'
        ]
        read_only_fields = ['id', 'review_user', 'movie_title','timestamp']
    
    def get_movie_title(self, obj):
        if isinstance(obj.content_object, Movie):
            return obj.content_object.title
        return None
    
    def get_likes_count(self, obj):
        return getattr(obj, "like_count", obj.likes.count())
    
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request, movie_pk=None):
        qs = self.get_queryset().filter(object_id=movie_pk)
        critic = qs.filter(is_critic=True).aggregate(avg=Avg('rating'), count=Count('id'))
        audience = qs.filter(is_critic=False).aggregate(avg=Avg('rating'), count=Count('id'))
        return Response({"critic": critic, "audience": audience})

    
    @action(detail=True, methods=['get'], url_path='heatmap')
    def heatmap(self, request, pk=None, movie_pk=None):
        qs = Review.objects.filter(object_id=movie_pk)
        data = qs.values(date=TruncDate('timestamp')).annotate(count=Count('id'))
        return Response(data)

  
    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request, movie_pk=None):
        qs = self.get_queryset().filter(object_id=movie_pk).annotate(likes_count=Count('likes')).order_by('-likes_count')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ReviewDetailSerializer(ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True) 
    class Meta:
        model=Review
        fields=['id','review_user','review_text','rating','is_critic','timestamp']
        read_only_fields=['id','review_user','timestamp']


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
    person=serializers.StringRelatedField()
    person_image = serializers.ImageField(source="person.profile_pic", read_only=True)
    class Meta:
        model=PersonRole
        fields=['id','person','role', 'character_name','movie','person_image']

class ActorRoleSerializer(ModelSerializer):
    person=serializers.StringRelatedField()
    person_image = serializers.ImageField(source="person.profile_pic", read_only=True)
    class Meta:
        model=PersonRole
        fields=['id','person','role', 'character_name','person_image']

class CrewRoleSerializer(serializers.ModelSerializer):
    person = serializers.StringRelatedField()
    movie=serializers.StringRelatedField()

    class Meta:
        model = PersonRole
        fields = [ 'id','person', 'role','movie']

class PersonSerializer(ModelSerializer):
    person_role=PersonalRoleSerializer(many=True,read_only=True) 
    class Meta:
        model=Person
        fields=['id', 'name', 'profile_pic', 'bio', 'birth_date', 'person_role']

#Movie Serializer

class MovieListSerializer(ModelSerializer):
    genres=serializers.StringRelatedField(many=True,read_only=True)
    trending_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model=Movie
        fields=['id','title','poster_image','release_date','genres','trending_score']

class MovieCreateSerializer(ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),many=True
        )
    languages = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), many=True
        )
    subtitles = serializers.PrimaryKeyRelatedField(
    queryset=Language.objects.all(), many=True
        )
    streaming_platform = serializers.PrimaryKeyRelatedField(
    queryset=Platform.objects.all(), many=True
        )
    class Meta:
        model=Movie
        fields=['title','poster_image','release_date','short_synopsis',
                'full_synopsis','trailer','runtime','genres','languages',
                'streaming_platform','subtitles']

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
        fields=['id','title','poster_image','backdrop_image','release_date','genres',
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

class MovieUpdateSerializer(ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True
    )
    languages = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), many=True
    )
    subtitles = serializers.PrimaryKeyRelatedField(
    queryset=Language.objects.all(), many=True
    )
    streaming_platform = serializers.PrimaryKeyRelatedField(
    queryset=Platform.objects.all(), many=True
    )
    class Meta:
        model=Movie
        fields=['title','short_synopsis','full_synopsis','release_date',
                'runtime','genres','languages','is_active','subtitles',
                'streaming_platform'] 


class MovieTriviaSerializer(ModelSerializer):
    movie=serializers.StringRelatedField(read_only=True)
    class Meta:
        model = MovieTrivia
        fields = ['id','fact','created_at','movie']

class GalleryImageSerializer(ModelSerializer):
    movie=serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GalleryImage
        fields = ['id','image_url','caption','uploaded_at','movie']

class BoxOfficeSerializer(ModelSerializer):
    class Meta:
        model = BoxOffice
        fields = "__all__"

class AwardSerializer(ModelSerializer):
    class Meta:
        model = Award
        fields = "__all__"

class FanTheorySerializer(ModelSerializer):
    class Meta:
        model = FanTheory
        fields = ['id','theory','upvotes','movie']
        read_only_fields = ['id', 'upvotes','movie']

class PollOptionSerializer(ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['id','option_text','votes']

class PollSerializer(ModelSerializer):
    options = PollOptionSerializer(many=True)
    class Meta:
        model = Poll
        fields = ['id','question','options']
    
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        for option in options_data:
            PollOption.objects.create(poll=poll, **option)
        return poll
    
    def update(self,instance, validated_data):
        options_data = validated_data.pop('options', None)
        instance.question = validated_data.get('question', instance.question)
        instance.save()
        
        if options_data is not None:
           
            instance.options.all().delete()
            for option in options_data:
                PollOption.objects.create(poll=instance, **option)

        return instance

# class ReviewSerializer(ModelSerializer):
#     user=serializers.StringRelatedField(read_only=True)
#     class Meta:
#         model=Review
#         fields=['user','review_text','rating','is_critic','timestamp']
# class MovieCastSerializer(ModelSerializer):
#     cast=ActorRoleSerializer
#     class Meta:
#         model=Movie
#         fields

