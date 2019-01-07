from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Forum, Thread, Post, LikeDislike, Notifications, ProfilePost
from .serializers import CategorySerializer, ForumSerializer, ThreadSerializer, PostSerializer
from django.contrib.auth.decorators import login_required
from .forms import ThreadForm, PostForm, ProfileForm, ProfilePostForm
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from itertools import chain
from django.utils import timezone

# Web Page Views
def category_page(request):
    categories = Category.objects.all()
    page_title = "Jellyfish Forum"
    page_description = "A forum made with Python and Django"
    return render(request, 'forum/categories.html', {'categories': categories, 'page_title': page_title, 'page_description': page_description})

def forum_page(request, pk):
    forum = get_object_or_404(Forum, pk=pk)
    page_title = forum.title
    page_description = forum.description
    canpostdiscussion = True
    return render(request, 'forum/forum.html', {'forum': forum, 'page_title': page_title, 'page_description': page_description, 'canpostdiscussion': canpostdiscussion})

def thread_page(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    unread_count = 0
    if request.user.is_authenticated:
        unread = Notifications.objects.filter(subscribed=request.user).exclude(actor=request.user).exclude(read=request.user)
        for notif in unread:
            if notif.content_type.model == 'post':
                if notif.content_object.ancestor.pk == thread.pk:
                    notif.read.add(request.user)
                    unread_count = unread_count +1
            elif notif.content_type.model == 'likedislike':
                if notif.content_object.post:
                    if notif.content_object.post.ancestor.pk == thread.pk:
                        notif.read.add(request.user)
                        unread_count = unread_count +1
                elif notif.content_object.thread:
                    if notif.content_object.thread.pk:
                        notif.read.add(request.user)
                        unread_count = unread_count +1
    page_title = thread.title
    page_description = "A discussion started by " + str(thread.actor)
    canreply = True
    subscribers = thread.subscribers.all()
    subscribed = False
    for subscriber in subscribers:
        if subscriber == request.user:
            subscribed = True
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.actor = request.user
                post.ancestor = thread
                post.highestancestor = thread.ancestor
                post.title = "Post by " + str(post.actor) + " in " + str(post.ancestor) + "."
                post.date = timezone.now()
                try:
                    if request.POST['subscribe'] == 'on':
                        thread.subscribers.add(request.user)
                except:
                    post.save()
                post.save()
                return redirect('thread_page', pk=thread.pk)
        else:
            form = PostForm()
            thread.views = thread.views + 1
            thread.save()
            return render(request, 'forum/thread.html', {'thread': thread, 'form': form, 'subscribed': subscribed, 'page_title': page_title, 'page_description': page_description, 'canreply': canreply, 'unread_count': unread_count})
    thread.views = thread.views + 1
    thread.save()
    return render(request, 'forum/thread.html', {'thread': thread, 'subscribed': subscribed, 'page_title': page_title, 'page_description': page_description, 'canreply': canreply, 'unread_count': unread_count})

def profile_page(request, pk):
    user = get_object_or_404(User, pk=pk)
    userprofile = True
    profile = user.profile
    if request.user.is_authenticated:
        if request.user == user:
            unread = Notifications.objects.filter(subscribed=request.user).exclude(actor=request.user).exclude(read=request.user)
            for notif in unread:
                if notif.content_type.model == 'profilepost':
                    notif.read.add(request.user)
    activities = list(chain(Post.objects.filter(actor=user), 
                            Thread.objects.filter(actor=user), 
                            LikeDislike.objects.filter(actor=user),
                            ProfilePost.objects.filter(profile=user.profile),
                            ProfilePost.objects.filter(actor=user).exclude(profile=user.profile)
                            ))
    activities.sort(key=lambda x: x.date, reverse=True)
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ProfilePostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.profile = profile
                post.actor = request.user
                post.title = str(request.user) + " posting on " + str(profile)
                post.date = timezone.now()
                post.save()
                return redirect('profile_page', pk=profile.pk)
        else:
            form = ProfilePostForm()
            return render(request, 'forum/profile_page.html', {'form': form, 'profile': profile, 'activities': activities, 'userprofile': userprofile})
    return render(request, 'forum/profile_page.html', {'profile': profile, 'activities': activities, 'userprofile': userprofile})

# Form Views

@login_required
def thread_new(request, pk):
    forum = get_object_or_404(Forum, pk=pk)
    page_title = "New Discussion"
    page_description = "Staring a new discussion in " + forum.title + "."
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ThreadForm(request.POST)
            if form.is_valid():
                thread = form.save(commit=False)
                thread.actor = request.user
                thread.ancestor = forum
                thread.date = timezone.now()
                thread.updated = timezone.now()
                thread.save()
                thread.subscribers.add(request.user)
                return redirect('thread_page', pk=thread.pk)
        else:
            form = ThreadForm()
            return render(request, 'forum/discussion.html', {'form': form, 'forum': forum, 'page_title': page_title, 'page_description': page_description})
    return redirect('/')

@login_required
def post_new(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    page_title = "New Reply"
    page_description = "Replying to " + thread.title + "."
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.actor = request.user
                post.ancestor = thread
                post.highestancestor = thread.ancestor
                post.title = "Post by " + str(post.actor) + " in " + str(post.ancestor) + "."
                post.date = timezone.now()
                try:
                    if request.POST['subscribe'] == 'on':
                        thread.subscribers.add(request.user)
                except:
                    post.save()
                post.save()
                return redirect('thread_page', pk=thread.pk)
        else:
            form = PostForm()
            return render(request, 'forum/post.html', {'form': form, 'thread': thread, 'page_title': page_title, 'page_description': page_description})
    return redirect('/')

@login_required
def profile_edit(request):
    page_title = "Edit your profile"
    page_description = "Give your profile some personality."
    if request.method == 'POST':
        form = ProfileForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('/')

    else:
        form = ProfileForm(instance=request.user.profile)

    context = {
        'form': form
    }

    return render(request, 'forum/edit_profile.html', {'form': form, 'page_title': page_title, 'page_description': page_description})
# Edit or Remove System

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    thread = post.ancestor
    user = None
    page_title = "Editing Reply"
    page_description = "Editing reply to " + thread.title + "."
    if request.user.is_authenticated:
        user = request.user.username
        if str(user) == str(post.actor):
            if request.method == "POST":
                form = PostForm(request.POST, instance=post)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.actor = request.user
                    post.date = post.date
                    post.save()
                    return redirect('thread_page', pk=thread.pk)
            else:
                form = PostForm(instance=post)
            return render(request, 'forum/post.html', {'form': form, 'thread': thread, 'page_title': page_title, 'page_description': page_description})
    return redirect('/')

@login_required
def thread_edit(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    forum = thread.ancestor
    user = None
    page_title = "Editing Thread"
    page_description = "Editing " + thread.title + "."
    if request.user.is_authenticated:
        user = request.user.username
        if str(user) == str(thread.actor):
            if request.method == "POST":
                form = ThreadForm(request.POST, request.FILES, instance=thread)
                if form.is_valid():
                    thread = form.save(commit=False)
                    thread.actor = request.user
                    thread.date = thread.date
                    thread.save()
                    return redirect('thread_page', pk=thread.pk)
            else:
                form = ThreadForm(instance=thread)
            return render(request, 'forum/discussion.html', {'form': form, 'forum': forum, 'page_title': page_title, 'page_description': page_description})
    return redirect('/')

@login_required
def thread_remove(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    forum = thread.ancestor
    user = None
    # Delete notifications that are related to the Thread
    notifs = Notifications.objects.all()
    likenotifs = Notifications.objects.all()
    posts = thread.posts.all()
    for notif in notifs:
        for post in posts:
            if notif.content_object == post:
                likes = post.likes.all()
                for likenotif in likenotifs:
                    for like in likes:
                        if likenotif.content_object == like:
                            likenotif.delete()
                notif.delete() 
    for likenotif in likenotifs:
        likes = thread.likes.all()
        for like in likes:
            if likenotif.content_object == like:
                likenotif.delete()
    if request.user.is_authenticated:
        user = request.user.username
        if str(user) == str(thread.actor):
            thread.delete()
    return redirect('forum_page', pk=forum.pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    thread = post.ancestor
    user = None
    notifs = Notifications.objects.all()
    likenotifs = Notifications.objects.all()
    for notif in notifs:
        if notif.content_object == post:
            likes = post.likes.all()
            for likenotif in likenotifs:
                for like in likes:
                    if likenotif.content_object == like:
                        likenotif.delete()
            notif.delete() 
    if request.user.is_authenticated:
        user = request.user.username
        if str(user) == str(post.actor):
            post.delete()
    return redirect('thread_page', pk=thread.pk)

# Like/Dislike System

def like_post(request, pk, tpk):
    post = get_object_or_404(Post, pk=pk)
    thread = get_object_or_404(Thread, pk=tpk)
    user = request.user
    likes = LikeDislike.objects.filter(post=post)
    for like in likes:
        if like.actor == user:
            if like.value == -1 or like.value == 0:
                like.value = 1
                like.save()
                return redirect('thread_page', pk=thread.pk)
            like.value = 0
            like.save()
            return redirect('thread_page', pk=thread.pk)
    like_dislike = LikeDislike()
    like_dislike.post = post
    like_dislike.actor = user
    like_dislike.value = 1
    like_dislike.save()
    return redirect('thread_page', pk=thread.pk)

def dislike_post(request, pk, tpk):
    post = get_object_or_404(Post, pk=pk)
    thread = get_object_or_404(Thread, pk=tpk)
    user = request.user
    likes = LikeDislike.objects.filter(post=post)
    for like in likes:
        if like.actor == user:
            if like.value == 1 or like.value == 0:
                like.date = timezone.now()
                like.value = -1
                like.save()
                return redirect('thread_page', pk=thread.pk)
            like.value = 0
            like.save()
            return redirect('thread_page', pk=thread.pk)
    like_dislike = LikeDislike()
    like_dislike.post = post
    like_dislike.actor = user
    like_dislike.value = -1
    like_dislike.date = timezone.now()
    like_dislike.save()
    return redirect('thread_page', pk=thread.pk)

def like_thread(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    user = request.user
    likes = LikeDislike.objects.filter(thread=thread)
    for like in likes:
        if like.actor == user:
            if like.value == -1 or like.value == 0:
                like.value = 1
                like.date = timezone.now()
                like.save()
                return redirect('thread_page', pk=thread.pk)
            like.value = 0
            like.save()
            return redirect('thread_page', pk=thread.pk)
    like_dislike = LikeDislike()
    like_dislike.thread = thread
    like_dislike.actor = user
    like_dislike.value = 1
    like_dislike.date = timezone.now()
    like_dislike.save()
    return redirect('thread_page', pk=thread.pk)

def dislike_thread(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    user = request.user
    likes = LikeDislike.objects.filter(thread=thread)
    for like in likes:
        if like.actor == user:
            if like.value == 1 or like.value == 0:
                like.value = -1
                like.date = timezone.now()
                like.save()
                return redirect('thread_page', pk=thread.pk)
            like.value = 0
            like.save()
            return redirect('thread_page', pk=thread.pk)
    like_dislike = LikeDislike()
    like_dislike.thread = thread
    like_dislike.actor = user
    like_dislike.value = -1
    like_dislike.date = timezone.now()
    like_dislike.save()
    return redirect('thread_page', pk=thread.pk)

# Notifications

def notifications(request):
    user = request.user
    notifs = Notifications.objects.filter(subscribed=user).exclude(actor=user)
    return render(request, 'forum/notifications.html', {'notifs': notifs})

@login_required
def subscribe(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    user = request.user
    try:
        subscriber = thread.subscribers.get(username=user.username)
    except:
        thread.subscribers.add(user)
        return redirect('thread_page', pk=thread.pk)

    if subscriber:
        thread.subscribers.remove(user)

    return redirect('thread_page', pk=thread.pk)

def marked(request, pk):
    notif = get_object_or_404(Notifications, pk=pk)
    user = request.user
    try:
        reader = notif.read.get(username=user.username)
    except:
        notif.read.add(user)
        return redirect('notifications')

    if reader:
        notif.read.remove(user)
        
    return redirect('notifications')

# API Serializer Views
@api_view(['get'])
def categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['get'])
def forums(request):
    forums = Forum.objects.all()
    serializer = ForumSerializer(forums, many=True)
    return Response(serializer.data)

@api_view(['get'])
def threads(request):
    threads = Thread.objects.all()
    serializer = ThreadSerializer(threads, many=True)
    return Response(serializer.data)

@api_view(['get'])
def posts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)
