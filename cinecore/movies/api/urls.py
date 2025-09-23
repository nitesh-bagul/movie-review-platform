from django.urls import path,include
from movies.api.views import (GenreViewSet,PlatformViewSet,LanguageViewSet,
                              PersonViewSet,PersonRolaViewSet,MovieViewSet,
                              ReviewViewSet,MovieTriviaViewSet,GalleryImageViewSet,
                              BoxOfficeViewSet,AwardViewSet,FanTheoryViewSet,
                              PollViewSet,related_movies)

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
# urlpatterns = [
#     # path('genre/',GenreViewSet.as_view(),name='genre-view'),
   
# ]

router=DefaultRouter()
router.register(r'genres',GenreViewSet,basename='genre',)
router.register(r'platforms',PlatformViewSet,basename='platform')
router.register(r'languages',LanguageViewSet,basename='language')
router.register(r'people',PersonViewSet,basename='person')
router.register(r'peoplerole',PersonRolaViewSet,basename='person-role') 
router.register(r'movies',MovieViewSet,basename='movie') 
router.register(r'reviews',ReviewViewSet,basename='reviews')



movies_router = routers.NestedSimpleRouter(router, r'movies', lookup='movie')
movies_router.register(r'reviews', ReviewViewSet, basename='movie-reviews')

movies_trivia_router  = routers.NestedSimpleRouter(router, r'movies', lookup='movie')
movies_trivia_router.register(r'trivia', MovieTriviaViewSet, basename='movie-trivia')

movies_gallery_router = routers.NestedSimpleRouter(router, r'movies', lookup='movie')
movies_gallery_router.register(r'gallery', GalleryImageViewSet, basename='movie-gallery')

movies_boxoffice_router = routers.NestedSimpleRouter(router, r'movies', lookup='movie')
movies_boxoffice_router.register(r'boxoffice', BoxOfficeViewSet, basename='movie-boxoffice')

movies_award_router = routers.NestedSimpleRouter(router, r'movies', lookup='movie')
movies_award_router.register(r'awards', AwardViewSet, basename='movie-award')


movies_fantheories_router = routers.NestedSimpleRouter(router, r'movies', lookup='movie')
movies_fantheories_router.register(r'fantheories', FanTheoryViewSet, basename='movie-theory')

movies_polls_router = routers.NestedSimpleRouter(router, r'movies', lookup='movie')
movies_polls_router.register(r'polls', PollViewSet, basename='movie-polls')




urlpatterns = [
    path('',include(router.urls)),
    path('', include(movies_router.urls)),
    path('',include(movies_trivia_router.urls)),
    path('',include(movies_gallery_router.urls)),
    path('',include(movies_boxoffice_router.urls)),
    path('',include(movies_award_router.urls)),
    path('',include(movies_fantheories_router.urls)),
    path('',include(movies_polls_router.urls)),

 
    path("movies/<int:movie_id>/related/", related_movies),
    # path("polls/<int:poll_id>/vote/", vote_poll),
]