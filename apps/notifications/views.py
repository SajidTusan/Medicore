from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    unread_count = notifications.filter(is_read=False).count()

    return render(
        request,
        "notifications/list.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_notification_read(request, notification_id):
    if request.method != "POST":
        return redirect("notifications:list")

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    if notification.link:
        return redirect(notification.link)

    return redirect("notifications:list")


@login_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)

    return redirect("notifications:list")