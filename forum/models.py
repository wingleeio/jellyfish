from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150)
    order = models.IntegerField(default=0)
    def publish(self):
        self.save()
    def __str__(self):
        return self.title
    class Meta:
        ordering = ('order',)

class Forum(models.Model):
    ancestor = models.ForeignKey('forum.Category', on_delete=models.CASCADE, null=True, related_name='forums')
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.IntegerField(default=0)
    def publish(self):
        self.save()
    def __str__(self):
        return self.title
    class Meta:
        ordering = ('order',)

class Thread(models.Model):
    ancestor = models.ForeignKey('forum.Forum', on_delete=models.CASCADE, null=True, related_name='threads')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    views = models.IntegerField(default=0)
    subscribers = models.ManyToManyField(User, related_name='threads')
    updated = models.DateTimeField(default=timezone.now)
    def publish(self):
        self.save()
    def __str__(self):
        return self.title
    class Meta:
       ordering = ('-updated',)

class Post(models.Model):
    ancestor = models.ForeignKey('forum.Thread', on_delete=models.CASCADE, null=True, related_name='posts')
    highestancestor = models.ForeignKey('forum.Forum', on_delete=models.CASCADE, null=True, related_name='posts')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    def publish(self):
        self.save()
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['date',]

class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(default='default.jpeg', upload_to='profile-img/')
    signature = models.TextField(max_length=500, blank=True)
    def __str__(self):
        return f'{self.user.username} Profile'
    def save(self):
        super().save()

class ProfilePost (models.Model):
    profile = models.ForeignKey('forum.Profile', on_delete=models.CASCADE, related_name="posts")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    content = models.TextField(max_length=300, blank=True)
    date = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-date',]
    def publish(self):
        self.save()
    def __str__(self):
        return self.title

class LikeDislike (models.Model):
    post = models.ForeignKey('forum.Post', on_delete=models.CASCADE, null=True, related_name="likes")
    thread = models.ForeignKey('forum.Thread', on_delete=models.CASCADE, null=True, related_name="likes")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    date = models.DateTimeField(default=timezone.now)
    value = models.IntegerField(default=0)
    def publish(self):
        self.save()
    def __str__(self):
        return str(self.actor) + " liked this."

class Notifications (models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_actor")
    subscribed = models.ManyToManyField(User, related_name='subscribed')
    date = models.DateTimeField(default=timezone.now, blank=True)
    read = models.ManyToManyField(User, related_name='read')
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    class Meta:
        ordering = ['-date',]
    def publish(self):
        self.save()
    def __str__(self):
        return str(self.actor) + " did " + str(self.content_type) + "."

@receiver(post_save, sender=Post)
def auto_notification (sender, instance, created, **kwargs):
    if created:
        actor = instance.actor
        action = instance
        targets = instance.ancestor.subscribers.all()
        new_notification = Notifications.objects.create(actor=actor, content_object=action)
        for target in targets:
            new_notification.subscribed.add(target)

@receiver(post_save, sender=ProfilePost)
def auto_notification_profile_post (sender, instance, created, **kwargs):
    if created:
        actor = instance.actor
        action = instance
        target = instance.profile.user
        new_notification = Notifications.objects.create(actor=actor, content_object=action)
        new_notification.subscribed.add(target)

@receiver(post_save, sender=LikeDislike)
def auto_notification_like_dislike (sender, instance, created, **kwargs):
    if created:
        actor = instance.actor
        action = instance
        if instance.post:
            target = instance.post.actor
        elif instance.thread:
            target = instance.thread.actor
        new_notification = Notifications.objects.create(actor=actor, content_object=action)
        new_notification.subscribed.add(target)

def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = Profile(user=user)
        user_profile.save()
post_save.connect(create_profile, sender=User)

def update_thread(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    raw = kwargs['raw']
    print(instance)
    if created and not raw:
        instance.ancestor.updated = instance.date
        instance.ancestor.save()
post_save.connect(update_thread, sender=Post)