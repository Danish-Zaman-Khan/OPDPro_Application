from django.conf import settings


def desktop_context(request):
    return {"desktop_mode": settings.OPD_LOCAL_DESKTOP}
