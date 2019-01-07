from django import template
from forum.models import Post, Thread, LikeDislike

register = template.Library()

@register.filter
def count_posts(user):
    return Post.objects.filter(actor=user).count() + Thread.objects.filter(actor=user).count()

@register.filter
def count_likes(post):
    likes = LikeDislike.objects.filter(post=post)
    like_total = 0
    for like in likes:
        like_total = int(like_total) + int(like.value)
    return int(like_total)

@register.filter
def up_is_active(post, user):
    likes = LikeDislike.objects.filter(post=post)
    for like in likes:
        if like.actor == user:
            if like.value == 1:
                return "has-text-primary"
    return "has-text-grey-light"

@register.filter
def down_is_active(post, user):
    likes = LikeDislike.objects.filter(post=post)
    for like in likes:
        if like.actor == user:
            if like.value == -1:
                return "has-text-danger"
    return "has-text-grey-light"

@register.filter
def num_is_active(post, user):
    likes = LikeDislike.objects.filter(post=post)
    for like in likes:
        if like.actor == user:
            if like.value == 1:
                return "has-text-primary"
            if like.value == -1:
                return "has-text-danger"
    return "has-text-grey-light"

# Count Likes for Threads

@register.filter
def thread_count_likes(thread):
    likes = LikeDislike.objects.filter(thread=thread)
    like_total = 0
    for like in likes:
        like_total = int(like_total) + int(like.value)
    return int(like_total)

@register.filter
def thread_up_is_active(thread, user):
    likes = LikeDislike.objects.filter(thread=thread)
    for like in likes:
        if like.actor == user:
            if like.value == 1:
                return "has-text-primary"
    return "has-text-grey-light"

@register.filter
def thread_down_is_active(thread, user):
    likes = LikeDislike.objects.filter(thread=thread)
    for like in likes:
        if like.actor == user:
            if like.value == -1:
                return "has-text-danger"
    return "has-text-grey-light"

@register.filter
def thread_num_is_active(thread, user):
    likes = LikeDislike.objects.filter(thread=thread)
    for like in likes:
        if like.actor == user:
            if like.value == 1:
                return "has-text-primary"
            if like.value == -1:
                return "has-text-danger"
    return "has-text-grey-light"

@register.filter
def user_rep(user):
    threads = Thread.objects.filter(actor=user)
    posts = Post.objects.filter(actor=user)
    reputation = 0
    for thread in threads:
        likes = LikeDislike.objects.filter(thread=thread)
        for like in likes:
            reputation = int(reputation) + int(like.value)
    for post in posts:
        likes = LikeDislike.objects.filter(post=post)
        for like in likes:
            reputation = int(reputation) + int(like.value)
    return reputation

# @register.simple_tag
# def notificationlist(user):
#     notifs = Notifications.objects.filter(subscribed=user).exclude(actor=user)
#     return notifs