from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Forum, Thread, Post

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class PostSerializer(ModelSerializer):
    actor = UserSerializer()
    class Meta:
        model = Post
        fields = '__all__'

class ThreadSerializer(ModelSerializer):
    posts = PostSerializer(many=True)
    class Meta:
        model = Thread
        fields = ('title','posts')

class ForumSerializer(ModelSerializer):
    threads = ThreadSerializer(many=True)
    class Meta:
        model = Forum
        fields = ('order','title','description','threads')

class CategorySerializer(ModelSerializer):
    forums = ForumSerializer(many=True)
    class Meta:
        model = Category
        fields = ('order','title','forums')
