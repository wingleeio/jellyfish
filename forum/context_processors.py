from .models import Notifications

def notifications_list(request):
    try:
        if hasattr(request, 'user'):
            return {
                'notifs': Notifications.objects.filter(subscribed=request.user).exclude(actor=request.user),
                'unread': Notifications.objects.filter(subscribed=request.user).exclude(actor=request.user).exclude(read=request.user),
            }
    except:
        return {}
    return {}

        
    