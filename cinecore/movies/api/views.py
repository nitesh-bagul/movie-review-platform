from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from movies.api.pagination import ReviewPagination
from django.core.cache import cache

from rest_framework_simplejwt.authentication import JWTAuthentication
from movies.models import (Genre,Platform,Language,Person,PersonRole,
                           Movie,Review,WebShow,WebSeason,Episode,MovieRole,
                           MovieTrivia,GalleryImage,BoxOffice,Award,FanTheory,
                           Poll,ReviewLike,FanTheoryVote,PollOption,PollVote)
from movies.api.serializer import (GenreSerializer,PlatformSerializer,
                                   LanguageSerializer,PersonSerializer,
                                   PersonalRoleSerializer,MovieListSerializer,
                                   MovieDetailSerializer,ReviewSerializer,MovieUpdateSerializer,
                                   MovieCreateSerializer,CrewRoleSerializer,
                                   ReviewDetailSerializer,MovieTriviaSerializer,
                                   GalleryImageSerializer,BoxOfficeSerializer,
                                   AwardSerializer,FanTheorySerializer,
                                   PollSerializer)
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
import django_filters
from rest_framework import filters

from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count,Avg
from django.db.models.functions import TruncDate

#permission
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly
from movies.api.permission import IsAdminOrReadonly,IsReviewUserOrReadOnly

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
    # permission_classes=[IsAdminOrReadonly]
    permission_classes=[IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'streaming_platform__name']
    pagination_class=ReviewPagination 
    
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
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        movie = self.get_object()
        
        timeline_data = []

        if movie.release_date:
            timeline_data.append({
                "event": "Release Date",
                "date": movie.release_date,
                "details": f"Released on {movie.release_date}"
            })

      
        platforms = movie.streaming_platform.all()
        for platform in platforms:
            timeline_data.append({
                "event": "Streaming Platform",
                "date": movie.release_date,  
                "details": f"Available on {platform.name}"
            })

        for award in movie.awards.all():
            timeline_data.append({
                "event": "Award",
                "date": date(award.year, 1, 1), 
                "details": f"{'Won' if award.won else 'Nominated for'} {award.name} ({award.category})"
            })

        return Response(sorted(timeline_data, key=lambda x: x['date']))
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        movies = []

        for movie in Movie.objects.all():
            critic_data = movie.reviews.filter(is_critic=True).aggregate(avg=Avg("rating"))
            audience_data = movie.reviews.filter(is_critic=False).aggregate(avg=Avg("rating"))

            critic_avg = critic_data["avg"] or 0
            audience_avg = audience_data["avg"] or 0

            
            score = (critic_avg * 0.6) + (audience_avg * 0.4)

           
            movie.trending_score = round(score, 4)
            movies.append(movie)

       
        movies_sorted = sorted(movies, key=lambda m: m.trending_score, reverse=True)[:8]

        serializer = MovieListSerializer(movies_sorted, many=True)
        return Response(serializer.data)

    
    @action(detail=True,methods=['GET','POST'])
    def reviews(self,request, *args, **kwargs):
        movie=self.get_object()
        if request.method=='GET':
            queryset=movie.reviews.all().order_by("-timestamp")
            
            paginator = ReviewPagination()  
            page = paginator.paginate_queryset(queryset, request)
            serializer = ReviewSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        elif request.method=='POST':
            serializer=ReviewSerializer(data=request.data)
            review_user=request.user
            review_queryset=movie.reviews.filter(review_user=review_user)
            if review_queryset.exists():
                raise ValidationError("You have already reviewed")  
            
            serializer.is_valid(raise_exception=True)
            serializer.save(content_object=movie,review_user=review_user)
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

class MovieTriviaViewSet(viewsets.ModelViewSet):
    queryset = MovieTrivia.objects.all()
    serializer_class = MovieTriviaSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk') 
        qs=MovieTrivia.objects.all()
        qs=qs.filter(movie_id=movie_id)
        return qs

class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk') 
        qs=GalleryImage.objects.all()
        qs=qs.filter(movie_id=movie_id)
        return qs

class BoxOfficeViewSet(viewsets.ModelViewSet):
    queryset = BoxOffice.objects.all()
    serializer_class = BoxOfficeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk') 
        qs=BoxOffice.objects.all()
        qs=qs.filter(movie_id=movie_id)
        return qs

class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk') 
        qs=Award.objects.all()
        qs=qs.filter(movie_id=movie_id)
        return qs

class FanTheoryViewSet(viewsets.ModelViewSet):
    queryset = FanTheory.objects.all()
    serializer_class = FanTheorySerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk') or self.request.query_params.get('movie')
        qs = FanTheory.objects.all()
        if movie_id:
            qs = qs.filter(movie_id=movie_id)
        return qs
    def perform_create(self, serializer):
        movie_id = self.kwargs.get('movie_pk')
        if not movie_id:
            raise ValidationError({"movie": "movie_pk missing in URL"})
        movie = Movie.objects.get(id=movie_id)
        serializer.save(user=self.request.user, movie=movie)
        
   
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    def perform_create(self, serializer):
        movie_id = self.kwargs.get('movie_pk')
        if not movie_id:
            raise ValidationError({"movie": "movie_pk missing in URL"})
        movie = Movie.objects.get(id=movie_id)
        serializer.save(user=self.request.user, movie=movie) 
        
    @action(detail=True, methods=["post"],permission_classes=[IsAuthenticatedOrReadOnly])
    def upvote(self, request, pk=None,**kwargs):
        theory = self.get_object()
        user = request.user

        vote, created = FanTheoryVote.objects.get_or_create(theory=theory, user=user)

        if vote.points >= 5:
            return Response({"status": "max_points_reached", "upvotes": theory.upvotes}, status=400)

        vote.points += 1  
        vote.save()

        total_points = sum(v.points for v in theory.votes.all())
        theory.upvotes = total_points
        theory.save()

        return Response({"status": "upvoted", "upvotes": theory.upvotes})

@api_view(["GET"])
def related_movies(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    related = Movie.objects.filter(genres__in=movie.genres.all()).exclude(id=movie.id).distinct()
    serializer = MovieListSerializer(related, many=True)
    return Response(serializer.data)

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk')
        qs = Poll.objects.all()
        if movie_id:
            qs = qs.filter(movie_id=movie_id)
        return qs

    @action(detail=True, methods=["post"])
    def vote(self, request,pk=None, movie_pk=None):
        # poll = self.get_object()
        poll = self.get_object() 
        print(poll)
        option_id = request.data.get('option_id')
        print(option_id)
        user = request.user
        if not option_id:
            return Response({"error": "option_id required"}, status=400)
        
        if PollVote.objects.filter(user=user, poll=poll).exists():
            return Response({"error": "You have already voted."}, status=400)
        
        try:
            option = poll.options.get(id=option_id)
        except PollOption.DoesNotExist:
            return Response({"error": "Option not found"}, status=404)
        PollVote.objects.create(user=user, poll=poll, option=option)
        option.votes += 1
        option.save()

        return Response({"option_id": option.id, "votes": option.votes})
#Review views
class ReviewView(viewsets.ModelViewSet):
    queryset=Review.objects.all()
    serializer_class=ReviewSerializer   
    permission_classes=[IsReviewUserOrReadOnly]
    

class ReviewFilter(django_filters.FilterSet):
    movie_id=django_filters.NumberFilter(method='filter_by_movie')
    webshow_id=django_filters.NumberFilter(method="filter_by_webshow")
    username =django_filters.CharFilter(field_name='review_user__username',lookup_expr='iexact')
    
    class Meta:
        model=Review
        fields=['movie_id','webshow_id','username']
    
    def filter_by_movie(self,queryset,name,value):
        movie_ct=ContentType.objects.get_for_model(Movie)
        return queryset.filter(content_type=movie_ct,object_id=value)
    
    def filter_by_webshow(self,queryset,name,value):
        webshow_ct=ContentType.objects.get_for_model(WebShow)
        return queryset.filter(content_type=webshow_ct,object_id=value)
    
         

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('review_user').all()
    # serializer_class=ReviewSerializer
    filter_backends=[DjangoFilterBackend]
    filterset_class=ReviewFilter
    permission_classes=[IsReviewUserOrReadOnly]
    pagination_class=ReviewPagination 
    # filterset_fields=['username']
    
    
    def get_serializer_class(self):
        if self.action=='list':
            return ReviewSerializer
        elif self.action=='create':
            return ReviewSerializer
        elif self.action=='retrieve':
            return ReviewDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewDetailSerializer
        return ReviewSerializer 
    def create(self, request, *args, **kwargs):
        data=request.data.copy()
        review_user=request.user
        content_type_id = data.get("content_type")
        object_id = data.get("object_id")
        try:
            ct = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            raise ValidationError("Invalid content type.")
        
        model_class = ct.model_class()
        if not model_class.objects.filter(id=object_id).exists():
            raise ValidationError("Object does not exist.")
        
        if Review.objects.filter(review_user=review_user, content_type=ct, object_id=object_id).exists():
            raise ValidationError("You have already reviewed this item.")
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(review_user=request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        review = self.get_object()
        user = request.user

        existing_like = ReviewLike.objects.filter(like_user=user, review=review).first()
        if existing_like:
            existing_like.delete()
            return Response({"detail": "Unliked"}, status=status.HTTP_200_OK)

        ReviewLike.objects.create(like_user=user, review=review)
        return Response({"detail": "Liked successfully"}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self,request,  movie_pk=None):
        movie_ct=ContentType.objects.get_for_model(Movie)
        movie_pk = request.query_params.get("movie_id")
        
        if not movie_pk:
            return Response({"error": "movie_id is required"}, status=400)
        reviews = (
            Review.objects.filter(content_type=movie_ct, object_id=movie_pk)
            .annotate(like_count=Count('likes'))
            .order_by('-like_count', '-timestamp')
        )
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='summary')
    def ratings_summary(self, request, movie_pk=None):
        reviews = Review.objects.filter(object_id=movie_pk)

        critic_stats = reviews.filter(is_critic=True).aggregate(
            avg=Avg('rating'), count=Count('id')
        )
        audience_stats = reviews.filter(is_critic=False).aggregate(
            avg=Avg('rating'), count=Count('id')
        )

        data = {
            "critic": {
                "avg": round(critic_stats["avg"], 1) if critic_stats["avg"] else 0,
                "count": critic_stats["count"]
            },
            "audience": {
                "avg": round(audience_stats["avg"], 1) if audience_stats["avg"] else 0,
                "count": audience_stats["count"]
            }
        }
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='heatmap')
    def heatmap(self,request,movie_pk=None):
        print(movie_pk)
        movie_ct=ContentType.objects.get_for_model(Movie)
        reviews=Review.objects.filter(content_type=movie_ct,object_id=movie_pk)
        heatmap_data=reviews.annotate(date=TruncDate('timestamp')
                                      ).values('date').annotate(count=Count('id')
                                      ).order_by('date')
        return Response(heatmap_data)
        
    
    
    
    
    
    # def get_queryset(self):
    #     queryset = Review.objects.select_related('user')
    #     print(queryset)
    #     movie_id=self.request.query_params.get('movie_id')
    #     print(movie_id)
    #     webshow_id=self.request.query_params.get('webshow_id')
    #     print(webshow_id)
    #     username=self.request.query_params.get('username')
    #     print(username)
        
        
    #     if movie_id:
    #         movie_id = movie_id.strip('/')
    #         print(type(movie_id)) 
    #         movie_ct=ContentType.objects.get_for_model(Movie)
    #         print(movie_ct)
    #         queryset=queryset.filter(content_type=movie_ct,object_id=int(movie_id))
           
        
    #     if webshow_id:
    #         webshow_id = webshow_id.strip('/')
    #         webshow_ct=ContentType.objects.get_for_model(WebShow)
    #         print(webshow_ct)
    #         queryset=queryset.filter(content_type=webshow_ct,object_id=int(webshow_id))
            
        
    #     if username:
    #         username=username.strip('/')
    #         queryset = queryset.filter(user__username=username)
        
    #     return queryset
            
       

        

