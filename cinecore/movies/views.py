from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .models import Movie,Review
from django.contrib.contenttypes.models import ContentType
import requests

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, "movies/movie_detail.html", {"movie_id": pk})

def review_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie_type = ContentType.objects.get_for_model(Movie)

    reviews = Review.objects.filter(
        content_type=movie_type,
        object_id=movie.id
    )

    return render(request, "reviews/reviews.html", {
        "movie": movie,
        "reviews": reviews,
        "movie_id": movie.id, 
    })

def movie_insights(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, "add_ones/movie_insights.html", {"movie_id": movie.id})

def home(request):
    return render(request,'home.html')

def register_page(request):
    return render(request, "register.html")

def movie_page(request):
    return render(request, "movie_page.html")