from django import forms
from .models import Thread, Post, Profile, ProfilePost
from django.contrib.auth.models import User

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ('title', 'content',)

class PostForm(forms.ModelForm):
    subscribe = forms.BooleanField(initial=True, required=False)
    class Meta:
        model = Post
        fields = ('content',)
        labels = {
            'content': ('Write a reply'),
            'subscribe': ('Subscribe'),
        }

class ProfileForm(forms.ModelForm):
    photo = forms.ImageField(required=False)
    class Meta:
        model = Profile
        fields = ('photo', 'signature',)

class ProfilePostForm(forms.ModelForm):
    class Meta:
        model = ProfilePost
        fields = ('content',)