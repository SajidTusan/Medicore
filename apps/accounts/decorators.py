from functools import wraps

from django.shortcuts import render


def role_required(*allowed_roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            if request.user.role not in allowed_roles:
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator