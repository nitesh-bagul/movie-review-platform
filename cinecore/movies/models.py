from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Genre(models.Model):
    name=models.CharField(max_length=100,unique=True)
    
    def __str__(self):
        return self.name


# Website / app link
class Platform(models.Model):
    name=models.CharField(max_length=100)
    logo_image=models.ImageField(upload_to='platform_logos/', 
                                 blank=True, null=True)
    website_link=models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class LanguageChoices(models.TextChoices):
    # Indian Regional Languages
    HINDI = "hindi", "Hindi"
    TAMIL = "tamil", "Tamil"
    TELUGU = "telugu", "Telugu"
    MALAYALAM = "malayalam", "Malayalam"
    KANNADA = "kannada", "Kannada"
    BENGALI = "bengali", "Bengali"
    MARATHI = "marathi", "Marathi"
    GUJARATI = "gujarati", "Gujarati"
    PUNJABI = "punjabi", "Punjabi"
    ODIA = "odia", "Odia"
    
    # Other Country / International Languages
    ENGLISH = "english", "English"
    FRENCH = "french", "French"
    SPANISH = "spanish", "Spanish"
    GERMAN = "german", "German"
    JAPANESE = "japanese", "Japanese"
    KOREAN = "korean", "Korean"
    CHINESE = "chinese", "Chinese"
    RUSSIAN = "russian", "Russian"

class MovieRole(models.TextChoices):
    ACTOR='actor','Actor'
    DIRECTOR='director','Director'
    WRITER='writer','Writer'
    PRODUCER = 'producer', 'Producer'
    CINEMATOGRAPHER = 'cinematographer', 'Cinematographer'
    MUSIC_DIRECTOR = 'music_director', 'Music Director'

class ShowStatus(models.TextChoices):
    ONGOING = 'ongoing', 'Ongoing'
    COMPLETED = 'completed', 'Completed'
    UPCOMING = 'upcoming', 'Upcoming'

class Language(models.Model):
    name = models.CharField(max_length=20, choices=LanguageChoices.choices,
                            unique=True)
    def __str__(self):
        return self.get_name_display()



class Person(models.Model):
    name=models.CharField(max_length=100)
    profile_pic=models.ImageField(upload_to='person_profiles/', 
                                  blank=True, null=True)
    bio=models.TextField(blank=True,null=True)
    birth_date=models.DateField(blank=True,null=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id=models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    review_text=models.TextField()
    rating=models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    is_critic=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id') 
    
    def __str__(self):
        return f"Review by {self.user.username} - {self.rating}/10"
    


class Movie(models.Model):
    title=models.CharField(max_length=100)
    short_synopsis=models.CharField(max_length=500)
    full_synopsis=models.TextField()
    release_date=models.DateField()
    poster_image=models.ImageField(upload_to='movie_posters/',blank=True, null=True)
    Backdrop_image=models.ImageField(upload_to='movie_backdrops/',blank=True, null=True)
    runtime=models.IntegerField()
    genres=models.ManyToManyField(Genre)
    reviews = GenericRelation(Review)
    languages=models.ManyToManyField(Language,related_name='movies')
    trailer=models.URLField(blank=True, null=True)
    subtitles=models.ManyToManyField(Language,related_name='movies_subtitles')
    streaming_platform=models.ManyToManyField(Platform,blank=True,null=True,default='Not streaming.')
    is_active=models.BooleanField(default=True)


    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'N/A'})"


class WebShow(models.Model):
    title=models.CharField(max_length=100)
    short_synopsis=models.TextField()
    full_synopsis=models.TextField()
    seasons_count=models.PositiveIntegerField()
    creator=models.ManyToManyField(Person,related_name='created_shows')
    languages=models.ManyToManyField(Language,related_name='shows')
    subtitles=models.ManyToManyField(Language,related_name='shows_subtitles')
    poster_image=models.ImageField(upload_to='show_posters/',blank=True, null=True)
    backdrop_image=models.ImageField(upload_to='show_backdrops/',blank=True, null=True)
    genres=models.ManyToManyField(Genre)
    is_active=models.BooleanField(default=True)
    trailer=models.URLField(blank=True, null=True)
    streaming_platform=models.ManyToManyField(Platform)
    status=models.CharField(max_length=20,choices=ShowStatus.choices,
                            default=ShowStatus.UPCOMING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviews = GenericRelation(Review)  
    
    def __str__(self):
        return f"WebShow: {self.title}"

class WebSeason(models.Model):
    webshow=models.ForeignKey(WebShow,on_delete=models.CASCADE, 
                              related_name='seasons')
    season_number=models.PositiveIntegerField()
    poster_image=models.ImageField(upload_to='season_posters/', 
                                   blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    total_episodes=models.IntegerField()
    release_date=models.DateField()
    reviews = GenericRelation(Review)  
    
    class Meta:
        unique_together = ('webshow', 'season_number')
    
    def __str__(self):
         return f"{self.webshow.title} - Season {self.season_number}"

class Episode(models.Model):
    season=models.ForeignKey(WebSeason,on_delete=models.CASCADE,
                             related_name='episodes')
    episode_number=models.PositiveIntegerField()
    title=models.CharField(max_length=150)
    reviews = GenericRelation(Review)
    description=models.TextField()
    release_date=models.DateField()
    thumbnail_img=models.ImageField(upload_to='episode_thumbnails/')
    runtime=models.IntegerField()
    
    class Meta:
        unique_together = ('season', 'episode_number') 
    
    def __str__(self):
        return f'{self.season.webshow.title} S{self.season.season_number}E{self.episode_number} - {self.title}'

    
class PersonRole(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE,related_name='person_role')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True,related_name='movie_role')
    webshow = models.ForeignKey(WebShow, on_delete=models.CASCADE, null=True, blank=True,related_name="webshow_role")
    role = models.CharField(max_length=20, choices=MovieRole.choices)
    character_name = models.CharField(max_length=100, blank=True, null=True)
    
      
    class Meta:
        unique_together = ('person', 'movie', 'webshow', 'role')
    
    def __str__(self):
        content = self.movie.title if self.movie else self.webshow.title
        return f"{self.person.name} - {self.get_role_display()} in {content}"