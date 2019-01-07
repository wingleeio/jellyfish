from django.contrib import admin
from .models import Category, Forum, Thread, Post, Profile, Notifications, LikeDislike

# Register your models here.
admin.site.register(Category)
admin.site.register(Forum)
admin.site.register(Thread)
admin.site.register(Post)

admin.site.register(Profile)

admin.site.register(Notifications)

admin.site.register(LikeDislike)