from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')
    else:
        notifications = []
    return {
        'notifications': notifications
    }


def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, read=False).count()
        return {'unread_notifications_count': count}
    return {}