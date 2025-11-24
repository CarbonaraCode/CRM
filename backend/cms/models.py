from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Page(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField() # In futuro qui si integra un editor HTML
    is_published = models.BooleanField(default=False)
    meta_description = models.CharField(max_length=160, blank=True)

    def __str__(self):
        return self.title

class BlogPost(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
