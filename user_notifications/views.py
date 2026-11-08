from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.urls import reverse
from .models import Notification
from usermanagement.models import CustomUser

# Show all notifications
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user_notifications/list.html', {'notifications': notifications})

# Show only unread notifications
@login_required
def unread_notifications(request):
    unread_notifications = Notification.objects.filter(user=request.user,read=False).order_by('-created_at')
    return render(request, 'user_notifications/unread_list.html', {'notifications': unread_notifications})

# Unified send_message view for new message and reply
@login_required
def send_message(request, recipient_pk=None, notification_pk=None):
    if not (request.user.is_staff and request.user.staff_role == 'admin'):
        return HttpResponseForbidden("Only clinic administrators can send or reply to messages.")

    # Determine recipient
    if recipient_pk:
        recipient = get_object_or_404(CustomUser, pk=recipient_pk)
    elif notification_pk:
        notification = get_object_or_404(Notification, pk=notification_pk, user=request.user)
        # The recipient for reply is the sender of that notification
        if not notification.sender:
            messages.error(request, "Cannot reply to this notification (no sender).")
            return redirect('user_notifications:list')
        recipient = notification.sender
    else:
        messages.error(request, "No recipient specified.")
        return redirect('user_notifications:list')

    # Prevent messaging self
    if request.user.pk == recipient.pk:
        messages.error(request, "You cannot message yourself.")
        return redirect('user_notifications:list')

    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            Notification.objects.create(
                user=recipient,
                sender=request.user,
                message=content,
                url=reverse('doctors:doctor_detail', kwargs={'pk': request.user.pk})
            )
            messages.success(request, "Message sent successfully.")
            return redirect('user_notifications:list')
        else:
            messages.error(request, "Message content cannot be empty.")

    context = {
        'recipient': recipient,
    }
    return render(request, 'user_notifications/send_message.html', context)

# Mark a notification as read
@login_required
def mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notif.read:
        notif.read = True
        notif.save()
    # Redirect to notification URL or fallback
    return redirect(notif.url or reverse('user_notifications:list'))

# Notification detail view
@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.read:
        notification.read = True
        notification.save()
    return render(request, 'user_notifications/notification_detail.html', {'notification': notification})
