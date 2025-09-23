from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.home, name="home"),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path("register/", views.register_page, name="register"),
    path("movies/", views.movie_page, name="movie_page"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:pk>/reviews/", views.review_detail, name="review_detail"),
    path('movies/<int:pk>/insights/', views.movie_insights, name='movie_insights'),
]