from .models import Notification

def send_notification(user, message, url=None):
    """
    Creates and saves a notification for the given user.
    :param user: User instance to notify
    :param message: Text of the notification
    :param url: Optional URL the notification links to
    """
    notification = Notification.objects.create(
        user=user,
        message=message,
        url=url
    )
    return notification
