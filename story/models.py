from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Author(models.Model):
    Username=models.OneToOneField(User,on_delete=models.CASCADE)
    Name=models.CharField(max_length=50)
    # Password=models.CharField(max_length=50)

    def __str__(self):
        return str(self.Username)
    
    @receiver(post_save, sender=User)
    def create_author(sender, instance, created, **kwargs):
        if created:
            Author.objects.create(Username=instance)


class Story(models.Model):
    category_choices=[
        ('pol','politics'),
        ('art','art_news'),
        ('tech','technology_new'),
        ('trivia','trivial_news')
    ]
    region_choices=[
        ('uk','United_Kingdom_news'),
        ('eu','European_news'),
        ('w','world_news'),
    ]
    Story_Headline=models.CharField(max_length=64)
    Story_Category=models.CharField(max_length=6,choices=category_choices,default='trivia')
    Story_Region=models.CharField(max_length=2,choices=region_choices,default='uk')
    Post_Date=models.DateTimeField(auto_now_add=True)
    Story_Details=models.CharField(max_length=512)
    Authors=models.ForeignKey(Author,on_delete=models.CASCADE)

    def __str__(self):
        return self.Story_Headline