from django.db import models
from tinymce.models import HTMLField
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# Create your models here.
User = get_user_model()


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_post_view"),
        ]

    def __str__(self):
        return self.user.username


class PostManager(models.Manager):
    def published(self):
        return self.filter(published_date__lt=timezone.now())


# class Author(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     profile_picture = models.ImageField()
#
#     def __str__(self):
#         return self.user.username


class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    overview = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    content = HTMLField()
    # comment_count=models.IntegerField(default=0)
    # view_count = models.IntegerField(default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    thumbnail = models.ImageField()
    categories = models.ManyToManyField(Category, blank=False)
    featured = models.BooleanField(default=False)
    published_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self, *args, **kwargs):
        return reverse('post-detail', kwargs={
            'id': self.id
        })  # view nme-post

    @property
    def get_comments(self, *args, **kwargs):
        return Comment.objects.filter(post=self).order_by('-timestamp')[:3]

    @property
    def comment_count(self, *args, **kwargs):
        return Comment.objects.filter(post=self).count()

    @property
    def view_count(self):
        return PostView.objects.filter(post=self).count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username
