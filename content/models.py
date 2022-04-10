from django.db import models

from society.models import Profile


def upload_path(instance, name):
    return f'user_{instance.author.login}/{name}'


class Illustration(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    game_title = models.CharField(max_length=64)
    image = models.ImageField(upload_to=upload_path)


class IllustrationLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, default=None)
    illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE, related_name='likes')


class Video(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    game_title = models.CharField(max_length=64)
    video = models.FileField(upload_to=upload_path)


class VideoLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, default=None)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')


class New(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    game_title = models.CharField(max_length=64)
    content = models.TextField()
    image = models.ImageField(upload_to=upload_path, blank=True, null=True, default=None)


class NewLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, default=None)
    new = models.ForeignKey(New, on_delete=models.CASCADE, related_name='likes')


class Review(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    game_title = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=upload_path, blank=True, null=True, default=None)


class ReviewLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, default=None)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
