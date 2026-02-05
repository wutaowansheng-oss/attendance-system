"""
Custom middleware to allow all onrender.com domains
"""

class AllowRenderDomainsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow any onrender.com domain
        host = request.get_host().split(':')[0]  # Remove port if present
        if host.endswith('.onrender.com') or host == 'localhost' or host == '127.0.0.1':
            # Temporarily add to ALLOWED_HOSTS for this request
            from django.conf import settings
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]
        
        response = self.get_response(request)
        return response
