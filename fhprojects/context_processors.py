from django.conf import settings

def fhweb(request):
    is_mobile = getattr(request, 'is_mobile', False)

    return {
        'GA_CODE': settings.GOOGLE_ANALYTICS,
        'is_mobile': is_mobile,
        'base_template': 'base_mobile.html' if is_mobile else 'base_conventional.html',
        }
